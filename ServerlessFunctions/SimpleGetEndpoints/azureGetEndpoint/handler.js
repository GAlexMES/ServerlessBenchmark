'use strict';

/* eslint-disable no-param-reassign */

module.exports.azureGetEndpoint = function (context) {
  context.log('JavaScript HTTP trigger function processed a request.');

  context.res = {
    // status: 200, /* Defaults to 200 */
    body: 'Hello, World!',
  };

  context.done();
};
