# encoding: UTF-8
import re;
import sys;
PY2 = sys.version_info[0] == 2

enable_progress=True

if PY2:
    import codecs

    open = codecs.open
else:
    open = open


def is_in_ipynb():
    try:
        cfg = get_ipython()
        return True
    except NameError:
        return False

is_ipynb=is_in_ipynb();


def is_str(s):
    if PY2:
        if isinstance(s, (str, unicode)):
            return True
    else:
        if isinstance(s, (str)):
            return True;
    return False;

def to_str(s):
    if PY2 and isinstance(s,unicode):
        return s;

    try:
        return str(s);
    except Exception as e:
        if PY2:
            return unicode(s);
        return 'to_str error:' + str(e);




def get_mount(generator,take=None,skip=0):
    i=0;
    for r in generator:
        i += 1;
        if i<skip:
            continue;
        if isinstance( take,int) and i>0  and i>take+skip:
            break;
        yield r;

def force_generate(generator,max_count=None):
    count=0;
    for r in generator:
        count+=1
        if max_count is not None and count>=max_count:
            break
    return count;

def foreach(generator,func):
    for r in generator:
        func(r)
        yield r;

def concat(generators):
    for g in generators:
        for r in g:
            yield r

def to_list(generator, max_count=None):
    datas=[]
    count = 0;
    for r in generator:
        count += 1
        datas.append(r);
        if max_count is not None and count >= max_count:
            break
    return datas;



def progress_indicator(generator,title='Position Indicator',count=2000):
    if not enable_progress:
        for r in generator:
            yield r
        return
    if is_ipynb:
        from ipy_progressbar import ProgressBar
        generator = ProgressBar(generator, title=title)
        generator.max = count;
        generator.start()
        for data in generator:
            yield data;
        generator.finish()
    else:
        id=0;
        for data in generator:
            print(title+' '+str(id))
            id+=1;
            yield data;
        print('task finished');

def revert_invoke(item,funcs):
    for i in range(0,len(funcs),-1):
        item=funcs[i](item);
    return item;

def get(generator, format='print', count=20,paras=None):
    if format == 'print' and not is_ipynb:
        import pprint
        for d in generator:
            pprint.pprint(d);
        return ;
    elif format=='keys':
        for d in generator:
            for k in paras:
                print ("%s:  %s "%(k, d.get(k,'None')))
    elif format == 'key':
        import pprint
        for d in generator:
            pprint.pprint(d.keys())
        return ;
    list_datas= to_list(progress_indicator(generator, count=count), max_count=count);
    if is_ipynb or format=='df':
        from  pandas import DataFrame
        return DataFrame(list_datas);
    else:
        return list_datas;

def format(form,keys):
    res=form;
    for i in range(len(keys)):
        res = res.replace('{' + to_str(i) + '}', to_str(keys[i]))
    return res;
def get_keys(generator,s):
    count=0;
    for r in generator:
        count+=1;
        if count<5:
            for key in r.keys():
                if not key.startswith('_'):
                    try:
                        setattr(s,key,key)
                    except Exception as e:
                        pass
        yield r

def repl_long_space(txt):
    spacere = re.compile("[ ]{2,}");
    spacern = re.compile("(^\r\n?)|(\r\n?$)")
    r = spacere.subn(' ', txt)[0]
    r = spacern.subn('', r)[0]
    return r;


def merge(d1, d2):
    for r in d2:
        d1[r] = d2[r];
    return d1;

def conv_dict(dic,para_dic):
    import copy
    dic=copy.copy(dic)
    for k,v in para_dic.items():
        if k==v:
            continue
        if k in dic:
            dic[v]=dic[k]
            del dic[k]
    return dic

def para_to_dict(para, split1, split2):
    r = {};
    for s in para.split(split1):
        s=s.strip();
        rs = s.split(split2);

        key = rs[0].strip();
        if len(rs) < 2:
            value=key
        else:
            value = s[len(key) + 1:].strip();
        if key=='':
            continue
        r[key] = value;
    return r;


def merge_query(d1, d2, columns):
    if isinstance(columns, str) and columns.strip() != "":
        if columns.find(":")>0:
            columns=para_to_dict(columns,',',':')
        else:
            columns = columns.split(' ');
    if columns is None:
        return d1;
    if isinstance(columns,list):
        for r in columns:
            if r in d2:
                d1[r] = d2[r];
    elif isinstance(columns,dict):
        for k,v in columns.items():
            d1[v]=d2[k]
    return d1;

import types

def tramp(gen, *args, **kwargs):
    g = gen(*args, **kwargs)
    while isinstance(g, types.GeneratorType):
        g=g.next()
    return g



def first_or_default(generator):
    for r in generator:
        return r;
    return None;

def query(data, key):
    if data is None:
        return key;
    if is_str(key) and key.startswith('[') and key.endswith(']'):
        key = key[1:-1];
        if key in data:
            return data[key];
        else:
            return None
    return key;



def variance(n_list):
    sum1=0.0
    sum2=0.0
    N=len(n_list);
    for i in range(N):
        sum1+=n_list[i]
        sum2+= n_list[i] ** 2
    mean=sum1/N
    var=sum2/N-mean**2
    return var;


def find_any(iter, filter):
    for r in iter:
        if filter(r):
            return True;
    return False;


def get_index(iter, filter):
    for r in range(len(iter)):
        if filter(iter[r]):
            return r;
    return -1;

def get_indexs(iter, filter):
    res=[]
    for r in range(len(iter)):
        if filter(iter[r]):
            res.append(r);
    return res

def cross(a, gene_func):
    for r1 in a:
        r1=dict.copy(r1);
        for r2 in gene_func(r1):
            for key in r2:
                r1[key] = r2[key]
                yield dict.copy(r1);


def mix(g1,g2):
    while True:
        t1 = g1.next()
        if t1 is None:
            pass;
        else:
            yield t1
        t2 = g2.next()
        if t2 is None:
            pass
        else:
            yield t2;
        if t1 is None and t2 is None:
            return

def cross_array(a,b,func):
    for i in a:
        for j in b:
            yield func(i,j)


def merge_all(a, b):
    while True:
        t1 = a.__next__()
        if t1 is None:
            return;
        t2 = b.__next__()
        if t2 is not None:
            for t in t2:
                t1[t] = t2[t];
        yield t1;


def append(a, b):
    for r in a:
        yield r;
    for r in b:
        yield r;

def get_type_name(obj):
    import inspect
    if inspect.isclass(obj):
        s=str(obj);
    else:
        s=str(obj.__class__);
    p=s.find('.');
    r= s[p+1:].split('\'')[0]
    return r;


class EObject(object):
    pass;



def convert_to_builtin_type(obj):
    d=  { key:value for key,value in obj.__dict__.items() if isinstance(value,(str,int,float,list,dict,tuple,EObject) or value is None)};
    return d

def dict_to_poco_type(obj):
    if isinstance(obj,dict):
        result=  EObject();
        for key in obj:
            v= obj[key]
            setattr(result,key,dict_to_poco_type(v))
        return result
    elif isinstance(obj,list):
        for i in range(len(obj)):
            obj[i]=dict_to_poco_type(obj[i]);

    return obj;


def dict_copy_poco(obj,dic):
    for key,value in obj.__dict__.items():
        if key in dic:
            if isinstance(dic[key], (str,int,float,unicode)):
                setattr(obj,key,dic[key])



def group_by_mount(generator, group_count=10, take=-1, skip=0):
    tasks = [];
    task_id=0

    while True:
        task = next(generator, None);
        if task is None:
            yield tasks[:]
            return
        tasks.append(task)
        if len(tasks) >= group_count:
            yield tasks[:];
            task_id = task_id + 1
            tasks=[]
        if task_id < skip:
            continue
        if take>=0 and task_id > take:
            break

if __name__ == '__main__':
    res= is_in_ipynb();
    print(res)
