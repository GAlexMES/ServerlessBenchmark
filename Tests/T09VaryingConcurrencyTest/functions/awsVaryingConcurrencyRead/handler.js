'use strict';

const { DataTypes } = require("sequelize");
const { Sequelize } = require('sequelize');

var uuid = require('uuid');
var moment = require('moment');

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
const DataModel = sequelize.define("varyingModel", {
    instanceId: DataTypes.UUID,
    firstAccess: DataTypes.TEXT,
    lastAccess: DataTypes.TEXT,
    numberOfAccesses: DataTypes.INTEGER,
});

module.exports.write = async (event) => {
    const instances = await DataModel.findAll();
    return {
        statusCode: 200,
        body: JSON.stringify(instances)
    }
};
