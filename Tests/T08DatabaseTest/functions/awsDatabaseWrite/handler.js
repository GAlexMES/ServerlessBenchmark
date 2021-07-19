'use strict';

const { DataTypes } = require("sequelize");
const { Sequelize } = require('sequelize');

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

let first = true

module.exports.awsWriteEndpoint = async (event) => {
    let statusCode = 200;
    if(first){
        first = false;
        statusCode = 202;
        console.log("new instance for "+event["queryStringParameters"]['counter'])
    }else{
        console.log("no new instance :)")
    }

    await DataModel.build({
        name: "A User",
        birthday: parseInt(event.queryStringParameters["counter"])
    }).save()

    return {
        statusCode,
        body: JSON.stringify({
            message: 'Hello, World!',
        })
    }
};
