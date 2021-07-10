'use strict';

const {DataTypes} = require("sequelize");
const { Sequelize } = require('sequelize');

const sequelize = new Sequelize(
    process.env.MYSQLDATABASE,
    process.env.MYSQLUSER,
    process.env.MYSQLPASS,
);

const DataModel = sequelize.define("model", {
    name: DataTypes.TEXT,
    birthday: DataTypes.INTEGER,
});

module.exports.awsReadAllEndpoint = async (event, context, callback) => {
    await DataModel.findAll().then(() => {
        callback(null, {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Hello, World!',
            }),
        })
    })
};
