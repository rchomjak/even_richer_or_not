
def coroutine(func):
    def ret_func(*args, **kwargs):
        __func = func(*args, **kwargs)
        next(__func)
        return __func
    return ret_func
