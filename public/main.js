new Vue({
    el: '#app',
    data: function () {
        return {
            message: 'no response yet',
            items: [],
            fields: [],
            sess: 0,
            info: null,
            imageHref: null,
            arr: null,
            vars: {X: [], y: []},
            selectedXVar: null,
            selectedYVar: null,
            imageKey: 0,
            clusters: 10,
            selectedColName: null,
            colNames: [],
            pageNum: 0,
            rowCount: 10,
        }
    },
    methods: {
        _run: function (cmd, params, success, silent = false) {
            const scope = this
            if (!silent) {
                scope._clearAll()
                scope.message = "just a moment..."
            }
            fetch('http://localhost:8080/process', {
                method: 'post', headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    cmd,
                    x: scope.selectedXVar,
                    y: scope.selectedYVar ? scope.selectedYVar : null,
                    params,
                    sess: scope.sess
                })
            }).then(function (response) {
                if (!response.ok) {
                    throw Error(response.statusText)
                }
                return response.json()
            }).then(function (jsonResponse) {
                let response = JSON.parse(jsonResponse)
                if (!silent) {
                    scope.message = response.message
                }
                if (response.success === true) {
                    if (response.vars) {
                        let oldVars = scope.vars
                        scope.vars = response.vars
                        // If there are any new vars, set those as selected in the dropdowns
                        if (response.vars.X) {
                            let newXVars = response.vars.X.filter(e => !oldVars.X.includes(e))
                            if (newXVars.length) {
                                scope.selectedXVar = newXVars[0]
                            }
                        }
                        if (response.vars.y) {
                            let newYVars = response.vars.y.filter(e => !oldVars.y.includes(e))
                            if (newYVars.length) {
                                scope.selectedYVar = newYVars[0]
                            }
                        }
                    }
                    success(response)
                }
            }).catch(function (error) {
                if (!silent) {
                    scope.message = error
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
            this.items = []
            this.imageHref = null
            this.arr = null
        },
        load: function () {
            const scope = this
            scope.selectedXVar = null
            scope.selectedYVar = null
            scope.vars = {X: [], y: []}
            this._run('load', null, function () {
                scope.message = 'Success'
            })
        },
        showTable: function () {
            const scope = this
            this._run('showTable', {pageNum: scope.pageNum, rowCount: scope.rowCount}, function (response) {
                let index = 0
                for (let df of response.data) {
                    [scope.items[index], scope.fields[index]] = scope.pythonDataframeToVueTable(df)
                    index++
                }
            })
        },
        describe: function () {
            const scope = this
            this._run('describe', null, function (response) {
                let index = 0
                for (let df of response.data) {
                    [scope.items[index], scope.fields[index]] = scope.pythonDataframeToVueTable(df)
                    index++
                }
            })
        },
        getInfo: function () {
            const scope = this
            this._run('info', null, function (response) {
                scope.message = response.data
            })
        },
        image: function () {
            const scope = this
            this._run('image', {row: scope.pageNum * scope.rowCount}, function (response) {
                scope.imageHref = response.data
                scope.imageKey++
            })
        },
        hist: function () {
            const scope = this
            this._run('hist', null, function (response) {
                scope.imageHref = response.data
                scope.imageKey++
            })
        },
        scatter: function () {
            const scope = this
            this._run('scatter', null, function (response) {
                scope.imageHref = response.data
                scope.imageKey++
            })
        },
        pca: function () {
            const scope = this
            this._run('pca', null, function (response) {
                scope.arr = response.data
            })
        },
        kmeans: function () {
            const scope = this
            this._run('kmeans', {clusters: scope.clusters}, function () {
                scope.message = 'Success'
            })
        },
        tsne: function () {
            const scope = this
            this._run('tsne', null, function () {
                scope.message = 'Success'
            })
        },
        tsneLite: function () {
            const scope = this
            this._run('tsneLite', null, function () {
                scope.message = 'Success'
            })
        },
        featureScale: function () {
            const scope = this
            this._run('featureScale', null, function () {
                scope.message = 'Success'
            })
        },
        cat2int: function () {
            const scope = this
            this._run('cat2int', {colName: scope.selectedColName}, function () {
                scope.message = 'Success'
            })
        }
    },
    watch: {
        selectedXVar() {
            const scope = this
            this._run('colNames', null, function (response) {
                if (response.data && response.data.length) {
                    scope.selectedColName = response.data[0]
                    scope.colNames = response.data
                }
                scope.message = 'Success'
            }, true)
        }
    }
})