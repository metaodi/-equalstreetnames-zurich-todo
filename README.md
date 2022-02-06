# equalstreetnames-zurich-todo

Streamlit application running on heroku: https://equalstreetnames-zurich-todo.herokuapp.com/

[![Screenshot](https://user-images.githubusercontent.com/538415/152497937-41d4def6-0890-4f8d-98cb-6d630922b775.png)](https://equalstreetnames-zurich-todo.herokuapp.com/)

The basic idea is to show streets from OpenStreetMap combined with data from the official Strassennamenverzeichnis and WikiData.
Ideally new links on WikiData are created (e.g. add a "named after" claim to a street).

To load the data. a github action is run regularly and the data uploaded as artifact.
These arrifacts are then downloaded to heroku.
