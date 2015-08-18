import csv

VOWELS = ['aa', 'ae', 'ah', 'ao', 'aw', 'ay', 'eh', 'er', 'ey', 'ih', 'iy', 'ow', 'oy', 'uh', 'uw']

f = open('allowables.csv')
freader = csv.reader(f)

allowables = {}
for row in freader:
    letter = row[0]
    phones = row[1:]
    allowables[letter] = phones

    for phone in phones:
        phone_schwa = phone.replace('ax','ah')
        if phone_schwa != phone:
            if phone_schwa not in allowables[letter]:
                allowables[letter].append(phone_schwa)

    phones = allowables[letter]
    for phone in phones:
        phone_restressed = phone.replace('0','2')
        if phone_restressed != phone:
            if phone_restressed not in allowables[letter]:
                allowables[letter].append(phone_restressed)
        phone_restressed = phone.replace('1','2')
        if phone_restressed != phone:
            if phone_restressed not in allowables[letter]:
                allowables[letter].append(phone_restressed)
    allowables[letter] = list(set(allowables[letter]))
    allowables[letter].sort()

f.close()

fout = open('allowables.csv','w')
fwriter = csv.writer(fout)
for letter in allowables:
    rowout = [letter]+allowables[letter]
    fwriter.writerow(rowout)
fout.close()
