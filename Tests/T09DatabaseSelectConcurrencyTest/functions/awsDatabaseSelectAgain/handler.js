'use strict';

const { Sequelize, DataTypes } = require('sequelize');

let first = true;

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

module.exports.selectAgain = async (event) => {
    let statusCode = 200;
    if(first){
        first = false;
        statusCode = 202;
        console.log("new instance for "+event["queryStringParameters"]['counter'])
    }else{
        console.log("no new instance :)")
    }
    const entry = await DataModel.findOne({ where: { birthday: Number(event["queryStringParameters"]['counter']) } });

    console.log("Found that entry:"+entry);
    return {
        statusCode,
        body: JSON.stringify({
            message: 'Hello, ' + entry,
        }),
    };
};

