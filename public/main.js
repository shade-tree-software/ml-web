new Vue({
    el: '#app',
    data: function () {
        return {
            message: 'no response yet',
            items: null,
            sess: 0,
            info: null,
            imageHref: null,
            arr: null,
            vars: {X: [], y: []},
            selectedXVar: null,
            selectedYVar: null,
        }
    },
    methods: {
        _run: function (cmd, success) {
            const scope = this
            scope._clearAll()
            scope.message = "just a moment..."
            fetch('http://localhost:8080/process', {
                method: 'post', headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({cmd, x: scope.selectedXVar, y: scope.selectedYVar, sess: scope.sess})
            }).then(function (response) {
                return response.json()
            }).then(function (jsonResponse) {
                let response = JSON.parse(jsonResponse)
                scope.message = response.message
                if (response.success === true) {
                    if (response.vars) {
                        scope.vars = response.vars
                        if (scope.selectedXVar === null && scope.vars.X) {
                            scope.selectedXVar = scope.vars.X[0]
                        }
                    }
                    success(response)
                }
            })
        },
        pythonDataframeToVueTable: function (df) {
            let rows = {}
            let fields = ['index']
            for (let [colName, colData] of Object.entries(df)) {
                let firstRow = true
                for (let [rowIndex, cellData] of Object.entries(colData)) {
                    if (!rows[rowIndex]) {
                        rows[rowIndex] = {index: rowIndex}
                    }
                    rows[rowIndex][colName] = cellData
                    if (firstRow) {
                        fields.push(colName)
                    }
                }
                firstRow = false
            }
            return [Object.values(rows), fields]
        },
        _clearAll() {
            this.message = null
            this.items = null
            this.imageHref = null
            this.arr = null
        },
        load: function () {
            const scope = this
            this._run('load', function () {
                scope.message = 'Success'
            })
        },
        getHead: function () {
            const scope = this
            this._run('head', function (response) {
                [scope.items, scope.fields] = scope.pythonDataframeToVueTable(response.data)
            })
        },
        describe: function () {
            const scope = this
            this._run('describe', function (response) {
                [scope.items, scope.fields] = scope.pythonDataframeToVueTable(response.data)
            })
        },
        getInfo: function () {
            const scope = this
            this._run('info', function (response) {
                scope.message = response.data
            })
        },
        hist: function () {
            const scope = this
            this._run('hist', scope.sess, function (response) {
                scope.imageHref = response.data
            })
        },
        tsne: function () {
            const scope = this
            this._run('tsne', function (response) {
                scope.imageHref = response.data
            })
        },
        pca: function () {
            const scope = this
            this._run('pca', function (response) {
                scope.arr = response.data
            })
        },
        kmeans: function () {
            const scope = this
            this._run('kmeans', function (response) {
                [scope.items, scope.fields] = scope.pythonDataframeToVueTable(response.data)
            })
        }
    }
})