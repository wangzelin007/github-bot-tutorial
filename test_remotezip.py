zip_file_url = 'https://artprodwus21.artifacts.visualstudio.com/A7b238909-6802-4b65-b90d-184bca47f458/5147fa83-336e-44ef-bbe0-c86b8ae86cbb/_apis/artifact/cGlwZWxpbmVhcnRpZmFjdDovL2F6Y2xpdG9vbHMvcHJvamVjdElkLzUxNDdmYTgzLTMzNmUtNDRlZi1iYmUwLWM4NmI4YWU4NmNiYi9idWlsZElkLzM3NTUvYXJ0aWZhY3ROYW1lL21ldGFkYXRh0/content?format=zip'

from remotezip import RemoteZip


# list artifacts['value'][0]['resource']['downloadUrl']
# with RemoteZip('https://artprodwus21.artifacts.visualstudio.com/A7b238909-6802-4b65-b90d-184bca47f458/5147fa83-336e-44ef-bbe0-c86b8ae86cbb/_apis/artifact/cGlwZWxpbmVhcnRpZmFjdDovL2F6Y2xpdG9vbHMvcHJvamVjdElkLzUxNDdmYTgzLTMzNmUtNDRlZi1iYmUwLWM4NmI4YWU4NmNiYi9idWlsZElkLzM3NTUvYXJ0aWZhY3ROYW1lL21ldGFkYXRh0/content?format=zip') as zip:
#     for zip_info in zip.infolist():
#         print(zip_info.filename)

# import requests, StringIO, zipfile
#
# remotezip = requests.get('https://artprodwus21.artifacts.visualstudio.com/A7b238909-6802-4b65-b90d-184bca47f458/5147fa83-336e-44ef-bbe0-c86b8ae86cbb/_apis/artifact/cGlwZWxpbmVhcnRpZmFjdDovL2F6Y2xpdG9vbHMvcHJvamVjdElkLzUxNDdmYTgzLTMzNmUtNDRlZi1iYmUwLWM4NmI4YWU4NmNiYi9idWlsZElkLzM3NTUvYXJ0aWZhY3ROYW1lL21ldGFkYXRh0/content?format=zip')
# zipinmemory = cStringIO.StringIO(remotezip.read())
# zipinmemory = io.BytesIO(remotezip.read())
# zip = zipfile.ZipFile(zipinmemory)
# for fn in zip.namelist():
#     if fn.endswith(".ranks"):
#         ranks_data = zip.read(fn)
#         for line in ranks_data.split("\n"):
#             print(line)
            # do something with each line

import requests, zipfile, io
r = requests.get(zip_file_url)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall("./tmp")