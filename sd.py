from PIL import Image
def run_code(code, name1, name2, inp):
    img = Image.open(name1)
    ctc=0
    cgk=0
    pol=[]
    flag=True
    # img.width - ширина картинки
    # img.height - высота картинки
    i = 0
    a=True
    while i < img.width:
        j = 0
        if flag==False:
            break
        while j < img.height:
            if ctc==len(code):
                flag=False
                break
            r, g, b = img.getpixel((i, j))
            if code[ctc] == ">":
                j+=1
            elif code[ctc] == "<":
                if j!=0:
                    j-=1
            elif code[ctc] == ".":
                print(r, g, b)
            elif code[ctc] == "r":
                r+=1
                r %= 256
            elif code[ctc] == "b":
                b+=1
                b %= 256
            elif code[ctc] == "g":
                g+=1
                g %= 256
            elif code[ctc] == "d":
                r-=1
                r %= 256
            elif code[ctc] == "e":
                b-=1
                b %= 256
            elif code[ctc] == "n":
                g-=1
                g %= 256
            elif code[ctc] == "R":
                print(r)
            elif code[ctc] == "B":
                print(b)
            elif code[ctc] == "G":
                print(g)
            elif code[ctc] == "D":
                if cgk<len(inp):
                    r=ord(inp[cgk])
                    r %=256
                    cgk+=1
            elif code[ctc] == "E":
                if cgk<len(inp):
                    b=ord(inp[cgk])
                    b %=256
                    cgk+=1
            elif code[ctc] == "N":
                if cgk<len(inp):
                    g=ord(inp[cgk])
                    g %=256
                    cgk+=1
            elif code[ctc] == "[":
                # Если условие ложно (сумма == 255), прыгаем вперед к соответствующей "]"
                if (r + g + b) == 255:
                    # Найти парную "]" и перепрыгнуть
                    balance = 1
                    while balance > 0:
                        ctc += 1
                        if code[ctc] == "[":
                            balance += 1
                        elif code[ctc] == "]":
                            balance -= 1
                else:
                    # Иначе просто запоминаем позицию начала цикла
                    pol.append(ctc)
                    
            elif code[ctc] == "]":
                # Если условие НЕ выполнено (сумма != 255), возвращаемся к "["
                if (r + g + b) != 255:
                    ctc = pol[-1]  # вернуться к началу цикла
                else:
                    pol.pop()  # выход из цикла, удаляем позицию из стека
            ctc+=1
            img.putpixel((i, j), (r, g, b))
        i += 1
    img.show()

    img.save(name2)
    return
