'use strict';

let first = true

module.exports.awsGetEndpoint = async(event, context) => {
  let statusCode = 200;
  if(first) {
    first = false;
    statusCode = 202;
  }


  return {
    statusCode: statusCode,
    body: JSON.stringify({
      message: 'Hello, World!',
    }),
  };
};
