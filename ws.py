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
            if data['cmd'] == 'load':
                self.sessions[sess] = ml.load_csv_as_df(sess)
                return json.dumps({'success': True})
            elif data['cmd'] == 'head':
                if sess in self.sessions:
                    df = self.sessions[sess]
                    return json.dumps({'success': True, 'data': df.head().to_dict()})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'describe':
                if sess in self.sessions:
                    df = self.sessions[sess]
                    return json.dumps({'success': True, 'data': df.describe().to_dict()})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'info':
                if sess in self.sessions:
                    df = self.sessions[sess]
                    buffer = io.StringIO()
                    df.info(buf=buffer)
                    return json.dumps({'success': True, 'data': buffer.getvalue()})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'hist':
                if sess in self.sessions:
                    df = self.sessions[sess]
                    path = ml.plot_hist(df, sess)
                    return json.dumps({'success': True, 'data': path})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'pca':
                if sess in self.sessions:
                    df = self.sessions[sess]
                    [df_pca, variance] = ml.pca(df)
                    self.sessions[sess] = df_pca
                    return json.dumps({'success': True, 'data': variance})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'tsne':
                if sess in self.sessions:
                    df = self.sessions[sess]
                    path = ml.plot_tsne(df, sess)
                    return json.dumps({'success': True, 'data': path})
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
