from bot.blueprints import github
import json


def test_get_file_from_github():
    etag, r = github.get_file_from_github(
        'https://raw.github.com/wangzelin007/github-bot-tutorial/dev-20220905/.github/azure-cli-bot-20220829.json')
    print(json.dumps(r, sort_keys=False, indent=4))
    print(etag)

def test_get_file_from_github_with_etag():
    etag, r = github.get_file_from_github(
        'https://raw.github.com/wangzelin007/github-bot-tutorial/dev-20220905/.github/azure-cli-bot-20220829.json',
        'W/"d63c0e83b4f7a8d1aa966b8a2a6c91d571b2967bcba35373c4ad3955e48ecde8"'
    )
    if r:
        print(json.dumps(r, sort_keys=False, indent=4))
    print(etag)


@github_bp.post('/set_cache')
def test_set_cache():
    data = request.json
    value = data['key']
    cache.set("foo", value)
    return f'set {value} success'


@github_bp.get('/get_cache')
def test_get_cache():
    ref = cache.get("foo")
    return ref


if __name__ == '__main__':
    test_get_file_from_github()
    test_get_file_from_github_with_etag()