import cherrypy
import mlTools
import json
import os.path
import io

ml = mlTools.MachineLearning()


class MyWebService(object):
    sessions = {}

    def __get_var_names(self, sess):
        return {'X': list(self.sessions[sess]['X'].keys()),
                'y': list(self.sessions[sess]['y'].keys())}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def process(self):
        data = cherrypy.request.json
        if 'cmd' in data.keys() and 'sess' in data.keys():
            sess = data['sess']
            x_var_name = data['x']
            y_var_name = data['y']
            params = data['params']
            if data['cmd'] == 'load':
                x, y = ml.load_csv_as_df(sess)
                self.sessions[sess] = {'X': {'X': x}, 'y': {}}
                if y is not None:
                    self.sessions[sess]['y']['y'] = y
                return json.dumps({'success': True, 'vars': self.__get_var_names(sess)})
            elif data['cmd'] == 'showTable':
                if sess in self.sessions:
                    start_row = params['rowCount'] * params['pageNum']
                    end_row = start_row + params['rowCount']
                    x_dict = self.sessions[sess]['X'][x_var_name].iloc[start_row:end_row, :].to_dict()
                    y_dict = None
                    if y_var_name is not None:
                        print(y_var_name)
                        y_dict = self.sessions[sess]['y'][y_var_name].iloc[start_row:end_row, :].to_dict()
                    return json.dumps({'success': True, 'data': list(filter(None, [x_dict, y_dict]))})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'describe':
                if sess in self.sessions:
                    x_dict = self.sessions[sess]['X'][x_var_name].describe().to_dict()
                    y_dict = None
                    if y_var_name is not None:
                        y_dict = self.sessions[sess]['y'][y_var_name].describe().to_dict()
                    return json.dumps({'success': True, 'data': list(filter(None, [x_dict, y_dict]))})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'info':
                if sess in self.sessions:
                    x_df = self.sessions[sess]['X'][x_var_name]
                    buffer = io.StringIO()
                    x_df.info(buf=buffer)
                    return json.dumps(
                        {'success': True, 'data': buffer.getvalue()})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'pca':
                if sess in self.sessions:
                    x_df = self.sessions[sess]['X'][x_var_name]
                    [df_pca, variance] = ml.pca(x_df)
                    self.sessions[sess]['X']['PCA'] = df_pca
                    return json.dumps({'success': True, 'vars': self.__get_var_names(sess), 'data': variance})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'tsneLite':
                if sess in self.sessions:
                    x_df = self.sessions[sess]['X'][x_var_name]
                    df_tsne = ml.tsne_lite(x_df)
                    self.sessions[sess]['X']['TSNE'] = df_tsne
                    return json.dumps({'success': True, 'vars': self.__get_var_names(sess)})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'tsne':
                if sess in self.sessions:
                    x_df = self.sessions[sess]['X'][x_var_name]
                    df_tsne = ml.tsne(x_df)
                    self.sessions[sess]['X']['TSNE'] = df_tsne
                    return json.dumps({'success': True, 'vars': self.__get_var_names(sess)})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'kmeans':
                if sess in self.sessions:
                    x_df = self.sessions[sess]['X'][x_var_name]
                    k_means = ml.kmeans(x_df, params['clusters'])
                    self.sessions[sess]['X']['KMeans_best_reps'] = k_means['best_reps']
                    self.sessions[sess]['X']['KMeans_best5'] = k_means['best5']
                    self.sessions[sess]['X']['KMeans_best20pct'] = k_means['best20']
                    self.sessions[sess]['X']['KMeans_dist'] = k_means['dist']
                    self.sessions[sess]['X']['KMeans_clusters'] = k_means['clusters']
                    self.sessions[sess]['y']['KMeans_best_reps_labels'] = k_means['best_reps_labels']
                    self.sessions[sess]['y']['KMeans_labels'] = k_means['labels']
                    self.sessions[sess]['y']['KMeans_best5_labels'] = k_means['best5labels']
                    self.sessions[sess]['y']['KMeans_best20pct_labels'] = k_means['best20labels']
                    return json.dumps(
                        {'success': True, 'vars': self.__get_var_names(sess)})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'hist':
                if sess in self.sessions:
                    x_df = self.sessions[sess]['X'][x_var_name]
                    path = ml.plot_hist(x_df, sess)
                    return json.dumps({'success': True, 'data': path})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'scatter':
                if sess in self.sessions:
                    x_df = self.sessions[sess]['X'][x_var_name]
                    y_df = None
                    if y_var_name is not None:
                        y_df = self.sessions[sess]['y'][y_var_name]
                    path = ml.scatter_plot(sess, x_df, y_df)
                    return json.dumps({'success': True, 'data': path})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'cat2int':
                if sess in self.sessions:
                    x_df = self.sessions[sess]['X'][x_var_name]
                    col_name = params['colName']
                    self.sessions[sess]['X']['Cat2Int'] = ml.cat2int(x_df, col_name)
                    return json.dumps(
                        {'success': True, 'vars': self.__get_var_names(sess)})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'colNames':
                if sess in self.sessions:
                    col_names = list(self.sessions[sess]['X'][x_var_name].columns)
                    return json.dumps(
                        {'success': True, 'data': col_names})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'featureScale':
                if sess in self.sessions:
                    x_df = self.sessions[sess]['X'][x_var_name]
                    self.sessions[sess]['X']['Feature Scaled'] = ml.feature_scale(x_df)
                    return json.dumps(
                        {'success': True, 'vars': self.__get_var_names(sess)})
                else:
                    return '{"success": false, "message": "Session does not exist"}'


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/public': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    cherrypy.quickstart(MyWebService(), '/', conf)
