'''
The purpose of this code is to clean and sort WALS.
Written by Richard Littauer. 

Released into the public domain like stocked trout into the sea.

The commands needed to run this file can be seen at the bottom of the file next
to the name_main function. 


Things to be improved upon:

    - The ethnologue parents function, while it sorts for immediate parent
      nodes, can't do more than that, and can't find the upper nodes. This
      means that when the languages mentioned aren't in the WALS data, there's
      not much left. Out of the top 9 parents that have more than 25 languages,
      only 28 languages are left after going back to WALS when the data has
      been cleaned to 15%. That's almost nothing.

      On the other hand, there's not much to be done about this. They .xml
      isn't in the ethnologue file we have, and involving this would involve
      adding in another document and crosschecking again. This can be done, but
      not neccessarily at the moment without that .xml file for the trees. If
      this is done, we can also integrate MultiTree. This is a good area for
      future work.

      Neither can you hard code in trees, which might be a nice idea.

    - Dictionaries would have been a better way to do this, if you want to
      speed it up. As for now, it works, so I don't much see the need.

      The code is also inefficient, as there is a lot of repeated code. It
      would be better to take some of this out of the arg if statements and
      into separate functions, but I haven't had the time to rework this entire
      code - and if it works, it works.

    - It would be nice to be able to select langauges and run a graph based on
      them, instead of doing all languages and then sorting through. It would
      also be nice to be able to selectively choose which languages you want to
      graph against which other ones, in order to test things such as contact.
      However, it is difficult to say whether we, or WALS, has enough
      diachronic data to show contact that couldn't simply be done with
      geographic distance, as large contact eras are, I assume, relatively
      recent (after the Age of Exploration.)

'''

import sys

datapoints_file = "datapoints.csv" # WALS data
languages_file = "languages.csv" # WALS language details, inc. ISO codes
ethnologue = "ethnologue.csv" # Ethnologue scraped data, 2005
distance_file = "distances.csv" # Distances file

w_genus_data = "w_genus_data.csv" # Data sorted by WALS hier. by genus
w_family_data = "w_family_data.csv" # Data sorted by WALS hier. by family
w_subfamily_data = "w_subfamily_data.csv" # WALS Data by subfamily hier

# This function reads in the file
def read_file(x):
    f = open(x, 'r+')
    lineList = f.readlines()
    return lineList

# Splits the lines, if you wish. Probably a good thing.
def split_lines(x, y):
    lineList = []
    for line in x:
        line = line.split(y)
        lineList.append(line)
    return lineList

# This is to make a centred language list. 
def centred(unsorted_list):
    
    # Make a new list, populate with centred thing
    centred_list = [unsorted_list[0]]

    # For the even rows, put after source language
    for x in range(1, len(unsorted_list), 2):
        centred_list.append(unsorted_list[x])

    # For the odd rows, do the opposite
    for y in range(2, len(unsorted_list), 2):
        centred_list.insert(0, unsorted_list[y])

    # Join the list together in order to allow for .write() later
    centred_list = ''.join(centred_list)
    return centred_list

# This figures out how sparse the data is. 
def sparse(input_file):

    # Open the file
    f = open(input_file)
    lineList = f.readlines()

    # The non-empty values, and the total amount
    values_filled = 0
    values_total = 0

    # For each language
    for line in range(1,len(lineList)):
        language = lineList[line][1:]
        language = language.split(',')

        # For each feature
        for x in language:

            # If not empty,add it on.
            if x != '':
                values_filled += 1

            # Add the total amount
            values_total += 1

    # Return a fraction. 
    print values_filled, values_total
    return float(values_filled) / (values_total) * 100

def long_lat_graph(wals_code, radius):

    # Open the files
    langList = split_lines(read_file(languages_file), '\t')
    distList = split_lines(read_file(distance_file), '\t')
    dataList = split_lines(read_file(datapoints_file), ',')


    language_dict = {}

    # Use the wals code to select the language
    for line in langList:
        lang_code = line[0].replace('\"', '')
        language_dict.setdefault(lang_code, line)

    # If it is in the file
    if language_dict.has_key(wals_code) is True:

        # Find the index for this language
        index = distList[0].index(wals_code)

        # Make a dictionary for the distance information
        dist_dict = {}

        # Find the distances for all languages, put it in the dictionary
        for x in range(1,len(distList[index])):
            if distList[index][x] != 'NA':
                dist_dict.setdefault(distList[0][x], distList[index][x].replace('\n',''))
            if distList[x][index] != 'NA':
                if distList[x][index] != '0.0':
                    dist_dict.setdefault(distList[0][x], distList[x][index].replace('\n',''))

        # For each distance language
        for key in dist_dict: 

            # If close enough, add in to the file
            if float(dist_dict[key]) <= float(radius):
                line = language_dict[key]

                # Insert the distance to the languages file line
                line.insert(2, dist_dict[key])
                values_filled = 0
                values_total = 0

                # Add in the amount of filling there is
                for x in range(1,len(dataList)):
                    if dataList[x][0] == key:
                        for x in dataList[x][1:]:
                            if x != '': values_filled += 1

                            # Add the total amount
                            values_total += 1

                # As a percentage
                line.insert(2, str(float(values_filled)/float(values_total)))

                # Amount total
                line.insert(2, str(values_total))

                # Amount used
                line.insert(2, str(values_filled))

                # Print
                output_file = 'geo-' + wals_code
                o  = open(output_file, 'a')
                line = ','.join(line)
                print line
                o.write(line)
                o.close





# Defines how you want to sort these things
def phylogenetic(input_file, lower_threshhold):

    # load languages, datapoints
    languagesList = split_lines(read_file(languages_file), '\t')
    dataList = split_lines(read_file(input_file), ',')

    # load a dict of Wals codes
    wals_code = ['wals_code',]
    for x in range(len(languagesList)):
        lang_code = languagesList[x][0].replace('\"', '')
        wals_code.append(lang_code)

    # make sure that all of the data is accounted for in wals_code
    for line in range(len(dataList)):
        if dataList[line][0] not in wals_code:
            print 'Something is broken'
            break


    # If we're dragging from Ethnologue and not WALS hierarchies
    if sys.argv[3] == 'e':
        print 'Using ethnologue for family relations.'

        # Open the ethnologue file 
        ethnoList = split_lines(read_file(ethnologue), '\t')
        root_list = []

        # Used to avoid printing twice, repetition
        final_code_list = []

        # For the terminal count, to show completion
        print_count = 0

        # For line in the WALS data
        for line in range(1,len(dataList)):

            # Cross check with the WALS language file
            for lines in range(1, len(languagesList)):
                # shimming
                lang_code = languagesList[lines][0].replace('\"', '')
                if dataList[line][0] == lang_code:

                    # convert to ISO code from the language file
                    iso_code = languagesList[lines][7].replace('\"',\
                            '').replace("\n", '')
                    root = []


                    # Cross check with the ethnologue file
                    for lines in range(1, len(ethnoList)):
                        if iso_code == ethnoList[lines][0]:

                            # Choose out the roots and parents from Ethnologue
                            root = ethnoList[lines][1]
                            parents = ethnoList[lines][2]
                    
                            # This makes a non-split line example
                            i = dataList[line]
                            #i.insert(0, root)
                            i = ','.join(i)

                            # This list will be used for centreing.
                            print_list = [i]


                            # If we're looking for the large root tree
                            if sys.argv[4] == 'root':

                                # Find all roots in E.
                                for lines in range(1, len(ethnoList)):


                                    if root == ethnoList[lines][1]:

                                        # For each root, find the ISO code
                                        new_e_iso_code = ethnoList[lines][0]


                                        # Take the new ISO codes back to the
                                        # Wals languaage list
                                        for a in range(1, len(languagesList)):
                                            # Shim for multiple ISO codes
                                            mult_codes = languagesList[a][7].replace('\"', '').replace("\n", '')
                                            mult_codes = mult_codes.split(' ')
                                            # shimming, selecting WALS code
                                            final_code = languagesList[a][0].replace("\"", '')

                                            # Compare, find the right one
                                            if new_e_iso_code in mult_codes:

                                                # For all of the WALS data
                                                for b in range(1, len(dataList)):

                                                    # Find the right line
                                                    if dataList[b][0] == final_code:

                                                        # If not already printed
                                                        if final_code not in \
                                                                final_code_list:

                                                            # Write to file
                                                            print_list.append(root\
                                                                    + ',' +\
                                                                    ','.join(dataList[b]))

                                                            # Update previous printing
                                                            final_code_list.append(final_code)

                                                            # For terminal.
                                                            print_count += 1
                                                            print print_count

                            # Open the file
                            h = 'e-' + sys.argv[4] + '-' + sys.argv[2] +\
                            '-' + sys.argv[5]

                            h = open(h, 'a')

                            if len(print_list) != 0:
                                #if len(print_list) >= int(lower_threshhold):
                                    h.write(centred(print_list))

                                    # Close the file.
                                    h.close()

                            # If we're looking for the smaller subfamily trees
                            if sys.argv[4] == 'parents':

                                # Find amount of immediate parent nodes
                                # repeated
                                parent_lines = 0

                                # For each language in Ethnologue
                                for lines in range(1, len(ethnoList)):

                                    #If the parent from above matches
                                    if parents == ethnoList[lines][2]:

                                        #Update the counter
                                        parent_lines += 1

                                        # Used in centreing the list
                                        print_list = [i]

                                        # For each root, find the ISO code
                                        new_e_iso_code = ethnoList[lines][0]

                                        # Take the new ISO codes back to the
                                        # Wals languaage list
                                        for a in range(1, len(languagesList)):
                                            # Shim for multiple ISO codes
                                            mult_codes = languagesList[a][7].replace('\"', '').replace("\n", '')
                                            mult_codes = mult_codes.split(' ')
                                            # shimming, selecting WALS code
                                            final_code = languagesList[a][0].replace("\"", '')

                                            # Compare, find the right one
                                            if new_e_iso_code in mult_codes:

                                                # For all of the WALS data
                                                for b in range(1, len(dataList)):

                                                    # Find the right line
                                                    if dataList[b][0] == final_code:

                                                        # If not already printed
                                                        if final_code not in \
                                                                final_code_list:

                                                            # Write to file
                                                            print_list.append(parents\
                                                                    + ',' +\
                                                                    ','.join(dataList[b]))

                                                            # Update previous printing
                                                            final_code_list.append(final_code)

                                                            # For terminal.
                                                            print_count += 1
                                                            print print_count

                                        # Open the file
                                        h = 'e-' + sys.argv[4] + '-' + sys.argv[2] +\
                                        '-' + sys.argv[5]

                                        h = open(h, 'a')

                                        if len(print_list) != 0:
                                            #if len(print_list) >= int(lower_threshhold):
                                            h.write(centred(print_list))

                                            # Close the file.
                                            h.close()


 

    # If we're dragging from WALS
    if sys.argv[3] == 'w':
        print 'Using WALS for family relations.'

        # Used to show in terminal what is happening 
        printed_codes = []
        print_count = 0

        # For every WALS data line
        for a in range(1, len(dataList)):

            # Find a code, shim it
            wals_code = dataList[a][0]
            wals_code = '\"' + wals_code + '\"'

            # Find the language line
            for c in range(1, len(languagesList)):
                if wals_code == languagesList[c][0]:

                    # Define family, Genus, and subfam per entry
                    latitude = languagesList[c][2]
                    longitude = languagesList[c][3]
                    family = languagesList[c][5]
                    genus = languagesList[c][4]
                    subfamily = languagesList[c][6]
                    source_fgsf = family + ',' + genus + ',' + subfamily

                    # If we're outputting a family grouping
                    if sys.argv[4] == "family":

                        # Makes a joined centre line
                        i = dataList[a]
                        i.insert(0, longitude)
                        i.insert(0, latitude)
                        i.insert(0, source_fgsf)
                        i.insert(0, source_fgsf)
                        #i.insert(0, family)
                        i = ','.join(i)

                        # Used in centreing the list
                        print_list = [i]

                        # For each entry in that family
                        for d in range(1, len(languagesList)):
                            if languagesList[d][5] == family:

                                # Go back to the WALS data
                                for e in range(1, len(dataList)):

                                        # Shim, find that entry
                                        fam_code = languagesList[d][0].replace('\"', '')
                                        if fam_code == dataList[e][0]:
                                            if fam_code not in printed_codes:

                                                # Define family, Genus, and subfam per entry
                                                latitude = languagesList[d][2]
                                                longitude = languagesList[d][3]
                                                family = languagesList[d][5]
                                                genus = languagesList[d][4]
                                                subfamily = languagesList[d][6]
                                                fgsf = family + ',' + genus + ',' + subfamily

                                                # Append to already printed codes
                                                printed_codes.append(fam_code)

                                                # Write to print list
                                                print_list.append(source_fgsf + \
                                                        ',' + fgsf + ',' + latitude +\
                                                        ',' + longitude + ','\
                                                        + ','.join(dataList[e]))

                                                # Update print count
                                                print_count += 1
                                                print print_count

                        # Open file
                        h = open(w_family_data, 'a')

                        # If not empty
                        if len(print_list) != 0:

                                # And it there are enough languages
                                if len(print_list) >= int(lower_threshhold):

                                    #print
                                    h.write(centred(print_list))

                        h.close()

                    # If we're outputting for genus
                    if sys.argv[4] == "genus":

                        # Makes a joined centre line
                        i = dataList[a]
                        i.insert(0, longitude)
                        i.insert(0, latitude)
                        i.insert(0, source_fgsf)
                        i.insert(0, source_fgsf)
                        #i.insert(0, genus)
                        i = ','.join(i)

                        # Used in centreing the list
                        print_list = [i]

                        # For each entry in that genus
                        for d in range(1, len(languagesList)):
                            if languagesList[d][4] == genus:

                                # Go back to the WALS data
                                for e in range(1, len(dataList)):

                                        # Shim, find that entry
                                        gen_code = languagesList[d][0].replace('\"', '')
                                        if gen_code == dataList[e][0]:
                                            if gen_code not in printed_codes: 

                                                # Define family, Genus, and subfam per entry
                                                latitude = languagesList[d][2]
                                                longitude = languagesList[d][3]
                                                family = languagesList[d][5]
                                                genus = languagesList[d][4]
                                                subfamily = languagesList[d][6]
                                                fgsf = family + ',' + genus + ',' + subfamily

                                                # Append to already printed codes
                                                printed_codes.append(gen_code)

                                                # Write to print list
                                                print_list.append(source_fgsf + \
                                                        ',' + fgsf + ',' + latitude +\
                                                        ',' + longitude + ','\
                                                        + ','.join(dataList[e]))

                                                # Update print count
                                                print_count += 1
                                                print print_count

                        # Open file
                        h = open(w_genus_data, 'a')

                        # If not empty
                        if len(print_list) != 0:

                                # And it there are enough languages
                                if len(print_list) >= int(lower_threshhold):

                                    #print
                                    h.write(centred(print_list))

                        h.close()

                    # If we're outputting for subfamily
                    if sys.argv[4] == "subfamily":

                        # Makes a joined centre line
                        i = dataList[a]
                        i.insert(0, longitude)
                        i.insert(0, latitude)
                        i.insert(0, source_fgsf)
                        i.insert(0, source_fgsf)
                        #i.insert(0, subfamily)
                        i = ','.join(i)

                        # Used in centreing the list
                        print_list = [i]

                        if len(subfamily) != 0:

                            printed_codes_sf = []

                            # For each entry in that subfamily
                            for d in range(1, len(languagesList)):
                                if languagesList[d][6] == subfamily:

                                    # Go back to the WALS data
                                    for e in range(1, len(dataList)):

                                            # Shim, find that entry
                                            subfam_code = languagesList[d][0].replace('\"', '')
                                            if subfam_code == dataList[e][0]:
                                                if subfam_code not in \
                                                printed_codes_sf:

                                                    # Define family, Genus, and subfam per entry
                                                    latitude = languagesList[d][2]
                                                    longitude = languagesList[d][3]
                                                    family = languagesList[d][5]
                                                    genus = languagesList[d][4]
                                                    subfamily = languagesList[d][6]
                                                    fgsf = family + ',' + genus + ',' + subfamily

                                                    # Append to already printed codes
                                                    printed_codes_sf.append(subfam_code)

                                                    # Write to print list
                                                    print_list.append(source_fgsf\
                                                            + ',' + fgsf + ',' + \
                                                            latitude + ',' + \
                                                            longitude + ',' + \
                                                            ','.join(dataList[e]))

                                                    # Update print count
                                                    print_count += 1
                                                    print print_count

                            # Open file
                            h = open(w_subfamily_data, 'a')

                            # If not empty
                            if len(print_list) != 0:

                                    # And it there are enough languages
                                    if len(print_list) >= int(lower_threshhold):

                                        h.write(centred(print_list))

                            h.close()


'''
This function will sort according to geographic distance

Geographical distance:
    Instead, going for a set number of languages with full data in a given
    area. This can be manually reset as desired. One should only run
    geographic() on cleaned data.

'''

def geographic(input_file, lower_threshhold, top_bound, top_bound_value):

    # Open files
    f = open(input_file, 'r+')
    g = open(distance_file, 'r+')

    # For printing in the terminal
    lines_sorted = 0

    # Makes a list of all of the languages in the distance file, for sorting.
    language_row = []
    geoList = split_lines(read_file(distance_file), '\t')
    for x in range(len(geoList[0])):
        code = geoList[0][x].replace('\n', '')
        language_row.append(code)

    # For each language in input file
    lineList = f.readlines()

    # Makes a list of each language in the cleaned input data.
    language_f_low = []
    for line in lineList:
        line = line.split(',')
        language_f_low.append(line[0])

    # For each language
    for line in lineList[1:]:
        line = line.split(',')
        line_index = line

        # Find the wals_code
        wals_code = line[0]

        # Find where it is in the distance file
        x = language_row.index(wals_code)

        # Make an empty list to be populated by language distances
        stored_values = []

        # For every distance measurement (all languages)
        for value in range(1, len(geoList[x])):
            # shim
            if geoList[x][value] != 'NA':
                if geoList[x][value] != '0.0':

                    # Append horiztonal distance measures
                    stored_values.append([value, float(geoList[x][value])])

            # shim
            if geoList[value][x] != 'NA':
                if geoList[value][x] != '0.0':

                # Make sure the crux value isn't repeated
                    if geoList[x][value] != geoList[value][x]:

                        # Append vertical distance measures
                        stored_values.append([value, float(geoList[value][x])])

        # Sort the values and their indices
        sorted_values = sorted(stored_values, key=lambda x: x[1])


        # The amount of languages searched through
        total_searched = 0

        # If we're measuring amounts of languages by radius
        if top_bound == 'radius':

            # The maximum amount allowable
            maximum_radius = top_bound_value

            # To be populated by the closest, non-sparse languages
            languages_list = []

            # Going through the sorted distance lists
            for y in sorted_values:

                # If the top bound hasn't been met yet, cont. Shim.
                if y[1] != float(0.0):
                    if int(y[1]) <= int(maximum_radius):

                        # If 25 are met, cut it off. The heat maps we're using
                        # won't accept much more.
                        if len(languages_list) <= int(24):

                            # If in the cleaned file
                            target_wals_code = language_row[y[0]]
                            if target_wals_code in language_f_low:

                                # Add to lang_list
                                languages_list.append(y)

                            # Add to the total amount known, to see sparseness
                            total_searched += 1

            # If there aren't enough languages that fit, delete entry
            if len(languages_list) <= int(lower_threshhold):
                languages_list = []

        # If we're measuring merely by amount near
        if top_bound == 'languages':

            # The amount in the area we'll take
            maximum_areal_languages = int(top_bound_value)

            # List to be populated by the chosen
            languages_list = []

            # Starting with the closest languages
            for y in sorted_values:

                # Shim
                if y[1] != float(0.0):

                    # If in cleaned data
                    target_wals_code = language_row[y[0]]
                    if target_wals_code in language_f_low:

                        # If we haven't got enough yet
                        if len(languages_list) <= int(maximum_areal_languages-1):

                            # Add it in.
                            languages_list.append(y)

                    # Add to the total amount known, to see sparseness
                    total_searched += 1

            # If there aren't enough.
            if len(languages_list) <= int(lower_threshhold):
                languages_list = []

        # Used in centreing the list
        langList = split_lines(read_file(languages_file), '\t')

        for x in langList[1:]:
            if x[0][1:4] == line_index[0]:
                # Define family, Genus, and subfam per entry
                family = x[5]
                genus = x[4]
                subfamily = x[6]
                fgsf = family + ',' + genus + ',' + subfamily + ','

        line_index.insert(0, fgsf)
        line_index.insert(1, line[0])
        line_index.insert(2, '0.0')
        line_index.insert(3, str(total_searched))
        line_index = ','.join(line_index)
        print_list = [line_index]

        # For the languages chosen
        for language in languages_list:

            for x in langList[1:]:
                if x[0][1:4] == language_row[language[0]]:
                    languages_line = x

                    # Define family, Genus, and subfam per entry
                    family = x[5]
                    genus = x[4]
                    subfamily = x[6]
                    fgsf = family + ',' + genus + ',' + subfamily + ','

                    # Find the WALS code
                    wals_code = language_row[language[0]]

                    # Find the index where its information lies
                    wals_index = language_f_low.index(wals_code)

                    print_list.append(fgsf + line[0] + ',' + str(language[1]) + ','  +\
                            str(total_searched) + ',' + lineList[wals_index])


        # Make the output name. 
        output_file = 'geo-' + sys.argv[2] + '-' + sys.argv[4][0] + '-' +\
        sys.argv[5]

        h = open(output_file, 'a')

        # If not empty
        if len(print_list) != 0:

                # And it there are enough languages
                if len(print_list) >= int(lower_threshhold):

                    #print
                    h.write(centred(print_list))


        h.close()


# This will be fully added an integrated when we've run a few more of the other
# ones and know more fully how the graphics look, and what we can do with them.

def phylogeo(input_file, lower_threshhold):
     f = open(input_file, 'r+')
     g = open(distance_file, 'r+')



'''
This function cleans the data based on the amount of values it has filled.
Note - this is not feature kind at the moment, but applies to all values.

input_file = datapoints_file.csv # For now, this is a good idea. Eventually, more.
lower_threshhold = .5 # Lowest amount of data permitted, as a percentage.
output_file = "clean_data.csv" # Must be specified in argv.
'''

def data_clean(lower_threshhold, input_file):

    # The name of the output file changes for variables involved
    output_file = 'clean-' + sys.argv[2].replace('.','') + '-' + sys.argv[3].replace('.csv', '')

    # Open files
    f = open(input_file, 'r+')
    l = open(output_file, 'a')
    lineList = f.readlines()

    # For printing on the terminal
    lines_printed = 0

    # For each language
    for line in lineList:
        line = line.split(',')
        values = 0

        # For each value recorded 
        for value in line:

            # If it isn't nothing, note that
            if value != '':
                values += 1

        # If it is more filled than the threshhold
        if values >= (float(lower_threshhold)*len(line)):
            # Write values
            l.write(','.join(line))

            # Print the amount of lines printed
            lines_printed += 1
    print "Lines printed: " + str(lines_printed) + "."

    # Close file
    l.close()



if __name__ == "__main__":

    # If we're cleaning the data
    # Examples:

    # python clean.py clean .3 datapoints.csv

    if sys.argv[1] == 'clean':
        data_clean(sys.argv[2], sys.argv[3])

    # If we're just going with the hierarchies
    # Examples:

    # python clean.py phy clean-25-datapoints e root
    # python clean.py phy clean-25-datapoints e parents
    # python clean.py phy clean-25-datapoints w family
    # python clean.py phy clean-25-datapoints w subfamily
    # python clean.py phy clean-25-datapoints w genus


    if sys.argv[1] == 'phy':
        print "Now sorting languages phylogenetically."
        phylogenetic(sys.argv[2], sys.argv[5])

    # If we're sorting by distance (must be cleaned first)
    # Examples:

    # python clean.py geo clean-25-datapoints 15 radius 500
    # python clean.py geo clean-25-datapoints 15 languages 25

    if sys.argv[1] == 'geo':
        print "Now sorting languages geographically."
        geographic(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

    # Not yet coded, and may not be. 
    if sys.argv[1] == 'pg':
        print "Now sorting with a mixture of phylogenetic and geographically."
        phylogeo(sys.argv[2], sys.argv[3])

    if sys.argv[1] == 'sparse':
        print sparse(sys.argv[2])

    if sys.argv[1] == 'GIS':
        long_lat_graph(sys.argv[2], sys.argv[3])

'''
Commands to use ---

Cleaning
python clean.py clean .5 datapoints.csv

Ethnologue
#python clean.py phy clean-5-datapoints e root 15
#python clean.py phy clean-30-datapoints e parents 15 #Suspect not working.

WALS
python clean.py phy clean-30-datapoints w family 15
python clean.py phy clean-30-datapoints w subfamily 15
python clean.py phy clean-30-datapoints w genus 15

Geography
python clean.py geo clean-5-datapoints 15 radius 500

#python clean.py geo clean-5-datapoints 15 languages 25

'''
