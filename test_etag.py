# 1. 客户端下载一个链接（Sample）;
# 2. 服务器返回Sample，Sample中记录Last-Modified/ETag标记;
# 3. 客户端再次下载这个链接，并将上次请求时服务器返回的Last-Modified/ETag一起传递给服务器;
# 4. 服务器检查该Last-Modified或ETag，并判断出该页面自上次客户端请求之后还未被修改，直接返回响应304和一个空的响应体。
