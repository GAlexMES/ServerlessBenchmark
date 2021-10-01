'use strict';
let first = true

module.exports.awsFunctionT7 = async(event, context) => {
  let statusCode = 200;
  if(first) {
    first = false;
    statusCode = 202;
  }


  let n = 35;
  var stringv = 0;
  if (event.queryStringParameters !== null && event.queryStringParameters !== undefined) {
        if (event.queryStringParameters.n !== undefined && 
            event.queryStringParameters.n !== null && 
            event.queryStringParameters.n !== "") {
            n = event.queryStringParameters.n;
        }
    }

    stringv = fib(n);
   
  return {
    statusCode: statusCode,
    body: JSON.stringify({
      message: '' + stringv,
    }),
  };

  // Use this code if you don't use the http event with the LAMBDA-PROXY integration
  // return { message: 'Go Serverless v1.0! Your function executed successfully!', event };
};

function fib(n){
  if(n < 2) return n;
  
  return fib(n - 1) + fib(n - 2);
}
