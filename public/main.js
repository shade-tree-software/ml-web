new Vue({
    el: '#app',
    data: function () {
        return {
            result: 'no response yet',
            items: null,
            sess: 0,
            info: null,
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
                        rows[rowIndex] = {index: parseInt(rowIndex)}
                    }
                    rows[rowIndex][colName] = cellData
                }
            }
            return Object.values(rows)
        },
        load: function () {
            const scope = this
            scope.info = null
            scope.items = null
            this.run('load', scope.sess, function (result) {
                scope.result = result.message
                if (result.success === true) {
                    scope.info = 'Success'
                }
            })
        },
        getHead: function () {
            const scope = this
            scope.info = null
            scope.items = null
            this.run('head', scope.sess, function (result) {
                scope.result = result.message
                if (result.success === true) {
                    scope.items = scope.pythonDataframeToVueTable(result.data)
                }
            })
        },
        getInfo: function () {
            const scope = this
            scope.info = null
            scope.items = null
            this.run('info', scope.sess, function (result) {
                scope.result = result.message
                if (result.success === true) {
                    scope.info = result.data
                }
            })
        }
    }
})