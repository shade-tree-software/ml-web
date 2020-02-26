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
            var_name = data['varName']
            if data['cmd'] == 'load':
                self.sessions[sess] = {'X_train': ml.load_csv_as_df(sess)}
                return json.dumps({'success': True, 'vars': list(self.sessions[sess].keys())})
            elif data['cmd'] == 'head':
                if sess in self.sessions:
                    df = self.sessions[sess][var_name]
                    return json.dumps(
                        {'success': True, 'vars': list(self.sessions[sess].keys()), 'data': df.head().to_dict()})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'describe':
                if sess in self.sessions:
                    df = self.sessions[sess][var_name]
                    return json.dumps(
                        {'success': True, 'vars': list(self.sessions[sess].keys()), 'data': df.describe().to_dict()})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'info':
                if sess in self.sessions:
                    df = self.sessions[sess][var_name]
                    buffer = io.StringIO()
                    df.info(buf=buffer)
                    return json.dumps({'success': True, 'vars': list(self.sessions[sess].keys()), 'data': buffer.getvalue()})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'hist':
                if sess in self.sessions:
                    df = self.sessions[sess][var_name]
                    path = ml.plot_hist(df, sess)
                    return json.dumps({'success': True, 'vars': list(self.sessions[sess].keys()), 'data': path})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'pca':
                if sess in self.sessions:
                    df = self.sessions[sess][var_name]
                    [df_pca, variance] = ml.pca(df)
                    self.sessions[sess]['X_train_PCA'] = df_pca
                    return json.dumps({'success': True, 'vars': list(self.sessions[sess].keys()), 'data': variance})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'tsne':
                if sess in self.sessions:
                    df = self.sessions[sess][var_name]
                    path = ml.plot_tsne(df, sess)
                    return json.dumps({'success': True, 'vars': list(self.sessions[sess].keys()), 'data': path})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'kmeans':
                if sess in self.sessions:
                    df = self.sessions[sess][var_name]
                    reps = ml.k_means(df)
                    self.sessions[sess]['KMeans_reps'] = reps
                    return json.dumps(
                        {'success': True, 'vars': list(self.sessions[sess].keys()), 'data': reps.head().to_dict()})
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
