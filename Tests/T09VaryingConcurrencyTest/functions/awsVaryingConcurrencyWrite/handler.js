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

let first = true
const id = uuid.v4()
let dateBaseEntity;

module.exports.write = async (event) => {
    await DataModel.sync()
    let statusCode = 200;
    if(first){
        first = false;
        statusCode = 202;
        dateBaseEntity = await DataModel.create({
            instanceId: id,
            firstAccess: moment().format('x'),
            lastAccess: moment().format('x'),
            numberOfAccesses: 1
        })
        await dateBaseEntity.save()
    }else{
        dateBaseEntity.numberOfAccesses = dateBaseEntity.numberOfAccesses + 1
        dateBaseEntity.lastAccess = moment().format('x')
        await dateBaseEntity.save()
        console.log("no new instance :)")
    }
    return {
        statusCode,
        body: JSON.stringify({
            message: 'Hello, World!',
        })
    }
};
