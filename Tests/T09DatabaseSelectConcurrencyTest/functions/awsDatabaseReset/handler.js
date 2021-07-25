'use strict';

const {DataTypes} = require("sequelize");
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

module.exports.reset = async (event, context, callback) => {
    await DataModel.destroy({truncate: true}).then(() => DataModel.sync()).then(() => {
        callback(null, {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Hello, World!',
            }),
        })
    })
};
