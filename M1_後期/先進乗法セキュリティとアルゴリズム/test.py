import pandas as pd
square = pd.DataFrame([14*i+j for i in range(14)] for j in range(14))
print(square)

area1_1 = square.iloc[0, 0:13]
area1_2 = square.iloc[0:13, 13]
area1_3 = square.iloc[13, 1:]
area1_4 = square.iloc[1:, 0]
print("area1_1 =", area1_1)
print("area1_2 =", area1_2)
print("area1_3 =", area1_3)
print("area1_4 =", area1_4)

area2_1 = square.iloc[1, 1:12]
area2_2 = square.iloc[1:12, 12]
area2_3 = square.iloc[12, 2:13]
area2_4 = square.iloc[2:13, 1]
print("area2_1 =", area2_1)
print("area2_2 =", area2_2)
print("area2_3 =", area2_3)
print("area2_4 =", area2_4)

area3_1 = square.iloc[2:12, 2]
area3_2 = square.iloc[2:12, 11]
print("area3_1 =", area3_1)
print("area3_2 =", area3_2)

area4_1 = square.iloc[2:12, 3]
area4_2 = square.iloc[2:12, 10]
print("area4_1 =", area4_1)
print("area4_2 =", area4_2)

area5_1 = square.iloc[2, 4:10]
area5_2 = square.iloc[4, 4:10]
area5_3 = square.iloc[6, 4:10]
area5_4 = square.iloc[8, 4:10]
area5_5 = square.iloc[10, 4:10]
print("area5_1 =", area5_1)
print("area5_2 =", area5_2)
print("area5_3 =", area5_3)
print("area5_4 =", area5_4)
print("area5_5 =", area5_5)

area6 = square.iloc[3, 4:10]
print("area6 =", area6)

area7 = square.iloc[5, 4:10]
print("area7 =", area7)

area8 = square.iloc[7, 4:10]
print("area8 =", area8)

area9 = square.iloc[9, 4:10]
print("area9 =", area9)

area10 = square.iloc[11, 4:10]
print("area10 =", area10)



square2 = pd.DataFrame([[100]*14]*14)
print("square =",square)
# square2.iloc[0, 0:13] = area1_1
# square2.iloc[0:13, 13] = area1_2
# square2.iloc[13, 1:] = area1_3
# square2.iloc[1:, 0] = area1_4

# square2.iloc[1, 1:12] = area2_1
# square2.iloc[1:12, 12] = area2_2
# square2.iloc[12, 2:13] = area2_3
# square2.iloc[2:13, 1] = area2_4

# square2.iloc[2:12, 2] = area3_1
# square2.iloc[2:12, 11] = area3_2

# square2.iloc[2:12, 3] = area4_1
# square2.iloc[2:12, 10] = area4_2

# square2.iloc[2, 4:10] = area5_1
# square2.iloc[4, 4:10] = area5_2
# square2.iloc[6, 4:10] = area5_3
# square2.iloc[8, 4:10] = area5_4
# square2.iloc[10, 4:10] = area5_5

# square2.iloc[3, 4:10] = area6

# square2.iloc[5, 4:10] = area7

# square2.iloc[7, 4:10] = area8

# square2.iloc[9, 4:10] = area9

# square2.iloc[11, 4:10] = area10
# print("square2 = ",square2)

num_un1 = 96
num_un2 = 20
num_un3 = 20
num_un4 = 30
num_un5 = 6
num_un6 = 6
num_un7 = 6
num_un8 = 6
num_un9 = 6
num_un10 = 1
for i in range(2):
    for j in range(12):
        square2.loc[i, j] = 1
        square2.loc[j, 13-i] = 1
        square2.loc[13-i, 2+j] = 1
        square2.loc[2+j,i] = 1

for i in range(2,12):
    square2.loc[i,2] = 2
    square2.loc[i,11] = 2

for i in range(2,12):
    square2.loc[i,3] = 3
    square2.loc[i,10] = 3

for i in range(4,10):
    square2.loc[2,i] = 4
    square2.loc[4,i] = 4
    square2.loc[6,i] = 4
    square2.loc[8,i] = 4
    square2.loc[10,i] = 4

for i in range(4,10):
    square2.loc[3,i] = 5

for i in range(4,10):
    square2.loc[5,i] = 6

for i in range(4,10):
    square2.loc[7,i] = 7

for i in range(4,10):
    square2.loc[9,i] = 8

for i in range(4,10):
    square2.loc[11,i] = 9


#     square2.loc[0, i] = 1/num_un1
#     square2.loc[i, 13] = 1/num_un1
# for i in range(1,14):
#     square2.loc[13, i] = 1/num_un1
#     square2.loc[i, 0] = 1/num_un1

# for i in range(1,12):
#     square2.loc[1, i] = 1/num_un2
#     square2.loc[i, 12] = 1/num_un2
# for i in range(2,13):
#     square2.loc[12, i] = 1/num_un2
#     square2.loc[i, 1] = 1/num_un2

# for i in range(2,12):
#     square2.loc[i, 2] = 1/num_un3
#     square2.loc[i, 11] = 1/num_un3

# for i in range(2,12):


print("square2 = \n",square2)

square3 = pd.DataFrame([i for i in range(196)] for j in range(10))
print("square3 = \n",square3)

noised_X = []
for idx, row in square3.iterrows():
    X_idx = pd.DataFrame(row.to_numpy().reshape(14,14).tolist())
    for i in range(14):
        for j in range(14):
            X_idx.loc[i,j] = 0
    X_idx = X_idx.values.reshape(196).tolist()
    noised_X.append(X_idx)
noised_X = pd.DataFrame(noised_X)
print("noised_X = \n",noised_X)





square2 = pd.DataFrame([[100]*7]*7)
print("square =\n",square2)
num_un1 = 24
num_un2 = 10
num_un3 = 3
num_un4 = 3
num_un5 = 3
num_un6 = 3
num_un7 = 3
num_un8 = 1
for i in range(1):
    for j in range(6):
        square2.loc[i, j] = 1
        square2.loc[j, 6-i] = 1
        square2.loc[6-i, 1+j] = 1
        square2.loc[1+j,i] = 1

for i in range(1,6):
    square2.loc[i,1] = 2
    square2.loc[i,5] = 2

for i in range(2,5):
    square2.loc[1,i] = 3
    square2.loc[2,i] = 4
    square2.loc[3,i] = 5
    square2.loc[4,i] = 6
    square2.loc[5,i] = 7
print("square2 = \n",square2)

square3 = pd.DataFrame([[100]*14]*14)
print("square3 = \n",square3)
num_un1 = 96
num_un2 = 40
num_un3 = 6
num_un4 = 6
num_un5 = 6
num_un6 = 6
num_un7 = 6
num_un8 = 6
num_un9 = 6
num_un10 = 6
num_un11 = 6
num_un12 = 6
num_un13 = 1

for i in range(2):
    for j in range(12):
        square3.loc[i, j] = 1
        square3.loc[j, 13-i] = 1
        square3.loc[13-i, 2+j] = 1
        square3.loc[2+j,i] = 1

for i in range(2,12):
    square3.loc[i,2] = 2
    square3.loc[i,3] = 2
    square3.loc[i,10] = 2
    square3.loc[i,11] = 2

for i in range(4,10):
    square3.loc[2,i] = 3
    square3.loc[3,i] = 4
    square3.loc[4,i] = 5
    square3.loc[5,i] = 6
    square3.loc[6,i] = 7
    square3.loc[7,i] = 8
    square3.loc[8,i] = 9
    square3.loc[9,i] = 10
    square3.loc[10,i] = 11
    square3.loc[11,i] = 12

print("square3 = \n",square3)