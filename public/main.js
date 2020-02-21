new Vue({
    el: '#app',
    data: function () {
        return {
            result: 'no response yet',
            items: null,
            sess: 0,
            info: null,
            imageHref: null
        }
    },
    methods: {
        run: function (cmd, sess, cb) {
            fetch('http://localhost:8080/process', {
                method: 'post', headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({cmd, sess})
            }).then(function (response) {
                return response.json()
            }).then(function (jsonData) {
                cb(JSON.parse(jsonData))
            })
        },
        pythonDataframeToVueTable: function(df) {
            let rows = {}
            for (let [colName, colData] of Object.entries(df)) {
                for (let [rowIndex, cellData] of Object.entries(colData)) {
                    if (!rows[rowIndex]) {
                        rows[rowIndex] = {index: rowIndex}
                    }
                    rows[rowIndex][colName] = cellData
                }
            }
            return Object.values(rows)
        },
        clearAll() {
            this.info = null
            this.items = null
            this.imageHref = null
        },
        load: function () {
            const scope = this
            this.clearAll()
            this.run('load', scope.sess, function (result) {
                scope.result = result.message
                if (result.success === true) {
                    scope.info = 'Success'
                }
            })
        },
        getHead: function () {
            const scope = this
            this.clearAll()
            this.run('head', scope.sess, function (result) {
                scope.result = result.message
                if (result.success === true) {
                    scope.items = scope.pythonDataframeToVueTable(result.data)
                }
            })
        },
        describe: function () {
            const scope = this
            this.clearAll()
            this.run('describe', scope.sess, function (result) {
                scope.result = result.message
                if (result.success === true) {
                    scope.items = scope.pythonDataframeToVueTable(result.data)
                }
            })
        },
        getInfo: function () {
            const scope = this
            this.clearAll()
            this.run('info', scope.sess, function (result) {
                scope.result = result.message
                if (result.success === true) {
                    scope.info = result.data
                }
            })
        },
        hist: function () {
            const scope = this
            this.clearAll()
            this.run('hist', scope.sess, function (result) {
                scope.result = result.message
                if (result.success === true) {
                    scope.imageHref = result.data
                }
            })
        }
    }
})