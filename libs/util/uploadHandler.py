#encoding=utf8

'''
文件操作
'''
def upload(file, path, name, mod):
    if file:
        destination = open(path + name, mod)
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()
        return True
    else:
        return False

