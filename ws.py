import cherrypy
import mlTools
import json
import os.path
import io

ml = mlTools.MachineLearning()


class MyWebService(object):
    sessions = {}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def process(self):
        data = cherrypy.request.json
        if 'cmd' in data.keys() and 'sess' in data.keys():
            sess = data['sess']
            x_var_name = data['x']
            y_var_name = data['y']
            if data['cmd'] == 'load':
                x, y = ml.load_csv_as_df(sess)
                self.sessions[sess] = {'X': {'X_train': x}, 'y': {}}
                if y is not None:
                    self.sessions[sess]['y']['y_train'] = y
                return json.dumps({'success': True, 'vars': {'X': list(self.sessions[sess]['X'].keys()),
                                                             'y': list(self.sessions[sess]['y'].keys())}})
            elif data['cmd'] == 'head':
                if sess in self.sessions:
                    df = self.sessions[sess]['X'][x_var_name]
                    return json.dumps(
                        {'success': True, 'data': df.head().to_dict()})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'describe':
                if sess in self.sessions:
                    df = self.sessions[sess]['X'][x_var_name]
                    return json.dumps(
                        {'success': True, 'data': df.describe().to_dict()})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'info':
                if sess in self.sessions:
                    df = self.sessions[sess]['X'][x_var_name]
                    buffer = io.StringIO()
                    df.info(buf=buffer)
                    return json.dumps(
                        {'success': True, 'data': buffer.getvalue()})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'hist':
                if sess in self.sessions:
                    df = self.sessions[sess]['X'][x_var_name]
                    path = ml.plot_hist(df, sess)
                    return json.dumps({'success': True, 'vars': {'X': list(self.sessions[sess]['X'].keys()),
                                                                 'y': list(self.sessions[sess]['y'].keys())},
                                       'data': path})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'pca':
                if sess in self.sessions:
                    df = self.sessions[sess]['X'][x_var_name]
                    [df_pca, variance] = ml.pca(df)
                    self.sessions[sess]['X']['X_train_PCA'] = df_pca
                    return json.dumps({'success': True, 'vars': {'X': list(self.sessions[sess]['X'].keys()),
                                                                 'y': list(self.sessions[sess]['y'].keys())},
                                       'data': variance})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'tsne':
                if sess in self.sessions:
                    x_df = self.sessions[sess]['X'][x_var_name]
                    y_df = None
                    if y_var_name is not None:
                        y_df = self.sessions[sess]['y'][y_var_name]
                    path = ml.plot_tsne(x_df, y_df, sess)
                    return json.dumps({'success': True, 'data': path})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'kmeans':
                if sess in self.sessions:
                    df = self.sessions[sess]['X'][x_var_name]
                    [labels, reps] = ml.k_means(df)
                    self.sessions[sess]['X']['KMeans_reps'] = reps
                    self.sessions[sess]['y']['KMeans_labels'] = labels
                    return json.dumps(
                        {'success': True, 'vars': {'X': list(self.sessions[sess]['X'].keys()),
                                                   'y': list(self.sessions[sess]['y'].keys())},
                         'data': reps.head().to_dict()})
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
