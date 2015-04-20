Umbel API
==============

## Overview

This project implements profile and brand affinity API. The following API are implemented

1. Create a User Profile
2. Create and delete brand affinity
3. List all brand affinities of a user
4. List all brand affinities of a brand
5. View brand information **Not required**
6. View profile information **Not required**

## Local environment setup

### Prerequisite
1. Python 2.7
2. virtualenv
3. virtualenvwrapper: this is not required but following instructions assume it's installed
4. Postgres


### Steps

1. Clone the project from github

        git clone git@github.com:linhvo/umbelapi.git
    
2. Create virtual environment

        mkvirtualenv umbelapi
        
    This will automatically switch the environment to umbelapi. For subsequent working sessions, you need to switch 
     manually by running
        
        workon umbelapi
        
3. Install requirements

        pip install -r requirements.txt
        
4. Database setup

    PosgreSQL is used for local environment as well as in heroku.
     
    + Run the following commands in psql console to create postgres user & database
        
            create user umbel;
            create database umbelapi;
            grant all on database umbelapi to umbel;
            alter user umbel CREATEDB;
    + In terminal, run the following command to initialize the database
        
            python manage.py syncdb
            
    It will ask if you want to setup a superuser. Type Yes and fill in with appropriate info
        
5. Load data
    
    Fixtures of 3600 brands and 1000 profiles are included. To load them, run
   
        python manage.py loaddata brands.json
        python manage.py loaddata profiles.json
   
    A script to populate affinities is also included. It'll randomly sample up to 100 brands and assign to 
each user. To run
   
        python manage.py populate_affinities
   
6. Run

    You can use Chrome Extension: Postman app to test the API
    
        DJANGO_DEBUG=True python manage.py runserver
        
        
        
## Test on Heroku

The project is deployed to heroku for testing convenience. The app url is: 
[http://umbel-api.herokuapp.com](http://umbel-api.herokuapp.com)

## Unit Test

To run unit tests
    
        python manage.py test

## API Documentation

A version of this documentation can be accessed at /docs/. This was implemented with Swagger

The following documentation specifies how these API meet the requirement of the project and provide sample 
curl requests. For model schemas, please refer to swagger docs

1. Create a User Profile
   
    + Method: POST
    + Endpoint: /api/v1/profiles/
    + Input: None since profiles don't contain any user data at this point
    + Output: 201 status if the profile is created successfully. The profile is returned in response body
    + Curl: 
        
            curl 'http://umbel-api.herokuapp.com/api/v1/profiles/' -X POST -H 'Content-Type: application/json' -H 'Accept: */*'

2. List all brand affinities of a profile
    + Method: GET
    + Endpoint: /api/v1/affinities/?profile_id=<PROFILE_ID>
    + Input: 
        + PROFILE_ID: query parameter. id of the profile whose affinities are being looked up 
    + Output: 
        + Success: 200 status code and a list of affinities. Each of which includes the id of the profile and the brand
        and a created timestamp
        + Error: 404 status code with 'Not Found' detail message if the profile doesn't exist
    + Curl: 
        
            curl 'http://umbel-api.herokuapp.com/api/v1/affinities/?profile_id=1' -X GET -H 'Content-Type: application/json' -H 'Accept: */*'

3. List all brand affinities of a brand
    + Method: GET
    + Endpoint: /api/v1/affinities/?brand_id=<BRAND_ID>
    + Input: 
        + BRAND_ID: query parameter. id of the brand whose affinities are being looked up 
    + Output: 
        + Success: 200 status code and a list of affinities.
        + Error: 404 status code with 'Not Found' detail message if the brand doesn't exist
    + Curl: 
        
            curl 'http://umbel-api.herokuapp.com/api/v1/affinities/?brand_id=1' -X GET -H 'Content-Type: application/json' -H 'Accept: */*'

4. Create affinity
    + Method: POST
    + Endpoint: /api/v1/affinities/
    + Input: 
        + Affinity object: Sent in request body as a json object with profile and brand field that points to the 
        corresponding profile and brand
    + Output: 
        + Success: 201 status code if affinity is created successfully. The affinity is returned in response body
        + Error: 400 status code will be returned for each for the following cases:
            + Either profile or brand is not found
            + If there has been an affinity between the provided brand & profile
    + Curl: 
        
            curl 'http://umbel-api.herokuapp.com/api/v1/affinities/' -X GET -H 'Content-Type: application/json' -H 'Accept: */*' --data-binary '{"profile":20, "brand":2}' --compressed

5. Delete affinity
    + Method: DELETE
    + Endpoint: /api/v1/affinities/<AFFINITY_ID>/
    + Input: 
        + AFFINITY_ID: query parameter. ID of the affinity object that we want to delete. This can be obtain by using 
        affinities listing API above
    + Output: 
        + Success: 204 status code without response body if the deletion is successful
        + Error: 404 status code with 'Not Found' detail message if the id is invali
    + Curl: 
        
            curl -X DELETE 'http://umbel-api.herokuapp.com/api/v1/affinities/49474/'
         
## Caching
 
Both read-only api are cached with 30 days timeout. With a long timeout, a robust cache invalidation scheme is required.
Besides Django Rest Framework, drf-extensions is used for its caching mechanism. All three models in the api have
post-save signals (Affinity also has post-delete) to automatically invalidate the correct cache.

### Cache Key Construction

drf-extensions allows very flexible cache key construction but post-save signal cannot easily compute a cache key because
it doesn't run as part of an API HTTP request so it doesn't have access to HTTP request object that is required for
cache key construction. 

To invalidate cached request, next request is made to construct a different key compared to its previous 
cache key. This allows invalidate the cache without actually clearing the old cache. A custom key bit is included
that read from an agreed-upon cache location and use the value stored in that location as part of the cache key. The 
value can be anything. For our purpose, it is set to current timestamp.

For example, each 'get brand affinities by profile' request will construct it cache key from usual fields from a request
like request params, user-agent, content type and language. It will also read 'profile_<PROFILE_ID>' key from the cache
where <PROFILE_ID> is the profile_id request parameters. If the cache doesn't have that key, it'll insert current timestamp
to it. To invalidate this API for this profile ID, we only need to insert new value to that key and drf-extensions will
compute a different key.

### Cache Invalidation
All that is left is to figure out what cache to clear when a profile, a brand or an affinity is updated. This is unsurprisingly
not trivial.

When a profile with id 5 is update, not only will we need to change the profile_5 but we also need to change all the 
brand_<id> for each of brands that this profile has affinity with. This is because when we retrieve affinities by one of
these brands, it will need to have the latest profile data. The reverse is true regarding brand update

When an affinity between profile with id 5 and brand with id 6 is created or deleted, we will need to clear profile_5  
and brand_6.
 
This approach will be very difficult to maintain when an update change multiple API. A much simpler approach is to set
a shorter timeout

## Limitations

1. I tried using django-filter but it doesn't support django 1.8. So I had to override get_queryset in my viewset
2. /affinities/ will list all brand affinities but it is not a required api. Cache invalidation for this api is not handled
correctly. To fix it, I'd need to use a profile_0 (or anything that's not a valid profile id) and brand_0 and always update
these 2 special locations whenever any profile or brand is updated
3. Since unique id is just the auto-incremented database PK, anyone can delete all affinities. To fix this, we'd need
to have authorization or at the least, use GUID in the API request
4. I decided to not include full profile and brand json in the affinity object. Only brand id, profile id, affinity id 
and its created timestamp are included. I played around with nested relationships as detailed [HERE](http://www.django-rest-framework.org/api-guide/relations/#nested-relationships)
but I would have to override create method because nested relationships are read-only.
5. Timeout could have been infinite because we have automatic cache invalidation
