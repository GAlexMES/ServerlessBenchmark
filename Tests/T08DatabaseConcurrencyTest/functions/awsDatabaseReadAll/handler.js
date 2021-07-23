'use strict';

const { Sequelize, DataTypes } = require('sequelize');

const sequelize = new Sequelize(
    process.env.DBDATABASE,
    process.env.DBUSER,
    process.env.DBPASS,
    {
        host: process.env.DBHOST,
        dialect: 'postgres',
        port: process.env.DBPORT
    }
);

// if the database does not have a model table do a DataModel.sync()
const DataModel = sequelize.define("model", {
    name: DataTypes.TEXT,
    birthday: DataTypes.INTEGER,
});

let first = true;

module.exports.awsReadAllConcurrentEndpoint = async (event) => {
    let statusCode = 200;
    if(first){
        first = false;
        statusCode = 202;
        console.log("new instance for "+event["queryStringParameters"]['counter'])
    }else{
        console.log("no new instance :)")
    }
    const allEntries = await DataModel.findAll()

    console.log("Found that many entries:"+allEntries.length);
    return {
        statusCode,
        body: JSON.stringify({
            message: 'Hello, ' +event["queryStringParameters"]['counter'],
        }),
    };
};
