import cherrypy
import housingTools
import json
import os.path
import io

h = housingTools.Housing()


class MyWebService(object):

    sessions = {}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def process(self):
        data = cherrypy.request.json
        if 'cmd' in data.keys() and 'sess' in data.keys():
            if data['cmd'] == 'load':
                self.sessions[data['sess']] = h.load_housing_data()
                return json.dumps({'success': True})
            elif data['cmd'] == 'head':
                if data['sess'] in self.sessions:
                    housing = self.sessions[data['sess']]
                    return json.dumps({'success': True, 'data': housing.head().to_dict()})
                else:
                    return '{"success": false, "message": "Session does not exist"}'
            elif data['cmd'] == 'info':
                if data['sess'] in self.sessions:
                    housing = self.sessions[data['sess']]
                    buffer = io.StringIO()
                    housing.info(buf=buffer)
                    return json.dumps({'success': True, 'data': buffer.getvalue()})
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
