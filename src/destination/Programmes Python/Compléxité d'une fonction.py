def conversion(n):
    h = n // 3600             #2
    m = (n - 3600*h) // 60    #4
    s = n % 60                #2
    return h,m,s
#T(n)=2+4+2=8=O(1)

def puissanceMoinsUn(n):
   if n%2==0:   #2
      res = 1   #1
   else: 
      res = -1 
   return res
#☺T(n)=2+1=3=O(1)

def sommeEntiers(n):
    somme = 0              #1
                           #2
    for i in range(n+1):   #  ]*(n+1)
                           #1 ]
        somme += i         #2 ]
    return somme
#T(n)=2+(n+1)*3=3*n+5=O(n)

def factorielle(n):
   fact = 1               #1
   i = 2                  #1
   while i <= n:          #2
      fact = fact * i     #2
      i = i + 1           #2
   return fact
#T(n)=1+1+(n-1)*(1+2+2)=2+(n-1)*5=2+5n+(-5)=O(n)

def triSelection(l):                        # On note n = len(l)
    for i in range(len(l)-1):               # 2(len et -)
                                            # *(n-1)
                                            # 1 (i=...)
        indMini=i                           # 1 ( = )
        for j in range(i+1,len(l)):         # 2 (+ et len)
                                            # *(n/2)
                                            #1 (j=...)
        if l[j]<l[indMini]:                 #3 (2*[] + 1 <)
                indMini=j                   #1
        l[i],l[indMini]=l[indMini],l[i]     #4
