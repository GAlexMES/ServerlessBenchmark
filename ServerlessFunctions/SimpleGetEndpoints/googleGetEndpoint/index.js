'use strict';

exports.googleGetEndpoint = (request, response) => {
  response.status(200).send('Hello World!');
};

exports.event = (event, callback) => {
  callback();
};