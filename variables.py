def getFreshLiTagFromList(index):
    lis = {'7894eer','rebs456','123Werb','Ced1235','as45','123','asda'}
    count = 0
    liElement = None
    for li in lis:
        print(li)
        if count > index:
            liElement = li
            break
            #return lis[index]
                #result = li
        count+=1
    return liElement

x = getFreshLiTagFromList(3)
print(x)