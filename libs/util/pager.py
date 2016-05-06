#coding=utf-8


class Pager():
    '''
    数据处理方法集合
    Created on 2012-9-5
    @author: kyou
    '''
    _pageArr = []
    _l_num = 2
    _r_num = 2
    _padding = 2
    _currPage = 1

    def __init__(self, pageArr, currPage):
        self._pageArr = pageArr
        self._currPage = currPage
        return

    def getRange(self):
        res = self._pageArr[:]
        if not self._pageArr:
            return self._pageArr
        if len(self._pageArr) <= self._l_num + self._r_num + 2 * self._padding:
            return self._pageArr
        if self._currPage > self._l_num + self._padding + 1:
            res.insert(self._l_num, "...")
        if self._currPage < len(self._pageArr) - self._r_num - self._padding:
            res.insert(len(res) - self._r_num, "...")

        left = res[:self._l_num + 1]
        right = res[-(self._r_num + 1):]
        middle = []
        for i in range(2 * self._padding + 1):
            num = self._currPage - self._padding + i
            if num in self._pageArr and num not in left and num not in right:
                middle.append(num)
        left.extend(middle)
        left.extend(right)
        return left
