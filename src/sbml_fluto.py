#!/usr/bin/python


import time
import xml.etree.ElementTree as etree
import clingo




# boundary_cond = {} # {id : bool}
# lb = 0
# ub = 0
# obj = 0

def main(all_args):

    time_start = time.time()

    draft_sbml   = all_args.draftnet
    repair_sbml  = all_args.repairnet
    output_file  = all_args.output
    seeds_file   = all_args.seeds

    try:
        draftnet, seeds, targets = readSBMLnetwork(draft_sbml, 'd')
    except IOError:
        print('Error while opening {0}. Please check the input file'.format(draft_sbml))
        quit()

    with open(output_file + '_draft.lp','w') as f:
        for fact in draftnet:
            #print fact
            f.write(str(fact) + '.\n')
        try:
            with open(seeds_file,'r') as h:
                seeds = h.read().splitlines()
                lpseeds = [clingo.Function('seed', [seed]) for seed in seeds]
                for fact in lpseeds:
                    f.write(str(fact) + '.\n')
            print('{0} topological seed(s) was(were) provided and will be added to the draft'.format(len(seeds)))

        except:
            pass
        print('Done writing draft facts in ' + output_file + '_draft.lp')


    if repair_sbml != None:
        try:
            repairnet = readSBMLnetwork(repair_sbml, 'r')[0]
        except IOError:
            print('Error while opening {0}. Please check the input file'.format(repair_sbml))
            quit()

        with open(output_file + '_repair.lp','w') as g:
            for fact in repairnet:
                g.write(str(fact) + '.\n')
        print('Done writing repair facts in ' + output_file + '_repair.lp')
    else:
        print('No repair SBML file was given as an input')


    print('Conversion completed in {0:.2f} seconds'.format(time.time() - time_start))

    return

def get_model(sbml):
    """ get the model of a SBML file"""
    model_element = None
    for e in sbml:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "model":
            model_element = e
            break
    return model_element

def get_listOfSpecies(model):
    """ get list of species (compounds) for a model in a SBML file """
    listOfSpecies = None
    for e in model:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "listOfSpecies":
            listOfSpecies = e
            break
    return listOfSpecies

def get_listOfReactions(model):
    """ get list of reactions for a model in a SBML file """
    listOfReactions = None
    for e in model:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "listOfReactions":
            listOfReactions = e
            break
    return(listOfReactions)

def get_listOfReactants(reaction):
    """ get list of reactants for a reaction in a SBML file """
    listOfReactants = None
    for e in reaction:
        if e.tag[0] == "{":
          uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "listOfReactants":
            listOfReactants = e
            break
    return listOfReactants

def get_listOfProducts(reaction):
    """ get list of products for a reaction in a SBML file """
    listOfProducts = None
    for e in reaction:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "listOfProducts":
            listOfProducts = e
            break
    return listOfProducts


def get_listOfParameters(reaction):
    """ get list of parameters for a reaction in a SBML file """
    listOfParameters = None
    for e in reaction:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        #print(tag)
        if tag == "kineticLaw":
            kineticLaw = e
            #print(kineticLaw)
            for ee in kineticLaw:
                if ee.tag[0] == "{":
                    uri, tag = ee.tag[1:].split("}")
                else:
                    tag = ee.tag
                #print(tag)
                if tag == "listOfParameters":
                    listOfParameters = ee
                    break
    return listOfParameters


def readSBMLnetwork(filename, prefix) :
    """ create lp facts for the network from SBML """

    lpfacts         = []
    tree            = etree.parse(filename)
    sbml            = tree.getroot()
    model           = get_model(sbml)
    listOfReactions = get_listOfReactions(model)
    listOfSpecies   = get_listOfSpecies(model)

    seeds = []
    targets = []
    objective_reactions = []
    species_data = {}
    added_species = []

    # lpfacts.add(Term(name,[name])

    # get list of species
    for e in listOfSpecies:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "species":
            speciesId = e.attrib.get("id")
            speciesBC = e.attrib.get("boundaryCondition")
            speciesCp = e.attrib.get("compartment")
            # only add seeds if the BC true compound is in the draft, not the repair database
            if speciesBC == "true" and prefix == 'd':
                seeds.append(speciesId)
                lpfacts.append(clingo.Function('metabolite', [speciesId, clingo.Function('s')]))
                if not speciesId in species_data:
                    species_data[speciesId] = {'compartment':speciesCp, 'boundaryCondition':speciesBC}
                else:
                    print('Error: compound ' + speciesId + 'is defined twice')
                    quit()
            else:
                if not speciesId in species_data:
                    species_data[speciesId] = {'compartment':speciesCp, 'boundaryCondition':speciesBC}
                else:
                    print('Error: compound ' + speciesId + 'is defined twice')
                    quit()
    # print(prefix)
    # print(species_data)

    # get list of reactions
    for e in listOfReactions:
        lb = None
        ub = None
        oc = None
        obj_fnct = False
        # define default values in case missing information
        default_lb = -99999
        default_ub = 99999
        default_oc = 0

        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "reaction":
            reactionId = e.attrib.get("id")

            # obtain list of parameters for linear programming part
            listOfParameters = get_listOfParameters(e)
            if listOfParameters == None and prefix == 'r':
                if e.attrib.get("reversible") == "false":
                    lb = 0
                else:
                    lb = default_lb
                ub = default_ub
                oc = default_oc
                print('set default parameters to repairDB reaction {0}'.format(reactionId))
            elif listOfParameters == None:
                print("Error in draft reaction: ",reactionId, "listOfParameters = None")
                quit()
            else:
                for ee in listOfParameters:
                    if ee.tag[0] == "{":
                        uri, tag = ee.tag[1:].split("}")
                    else:
                        tag = ee.tag
                    if tag == "parameter":
                        paramId = ee.attrib.get("id")
                        paramValue = ee.attrib.get("value")

                        if paramId == "LOWER_BOUND":
                            lb = int(paramValue)
                        elif paramId == "UPPER_BOUND":
                            ub = int(paramValue)
                        elif paramId == "OBJECTIVE_COEFFICIENT":
                            oc = int(paramValue)
                            if oc == 1:
                                objective_reactions.append(reactionId)
                                obj_fnct = True

            # check whether a parameter is found for lb, ub and oc, otherwise
            # set it to default value + tell user
            if lb == None:
                lb = default_lb
                print("Had to set lower bound to default value" + str(default_lb) + "for reaction " + reactionId)

            if ub == None:
                ub = default_ub
                print("Had to set upper bound to default value " + str(default_ub) + " for reaction " + reactionId)

            if (lb < 0 and ub > 0) or (lb > 0 and ub < 0):
                lpfacts.append(clingo.Function('reversible', [reactionId]))

            if oc == None:
                oc = default_oc
                print("Had to set objective coefficient to default value " + str(default_oc) + " for reaction " + reactionId)

            # make facts for an objective reaction
            if obj_fnct and prefix == 'd':
                lpfacts.append(clingo.Function('reaction', [reactionId,clingo.Function('t')]))
                lpfacts.append(clingo.Function('objective', [reactionId,clingo.Function('t')]))
                lpfacts.append(clingo.Function('bounds', [reactionId,str(lb),str(ub)]))

            # make facts for a regular reaction
            else:
                lpfacts.append(clingo.Function('reaction', [reactionId,clingo.Function(prefix)]))
                lpfacts.append(clingo.Function('objective', [reactionId,clingo.Function(prefix)]))
                lpfacts.append(clingo.Function('bounds', [reactionId,str(lb),str(ub)]))

            # get reactants of considered reactin
            listOfReactants = get_listOfReactants(e)
            # exit with error if no reactant for an objective function
            if listOfReactants== None and obj_fnct == True:
                print("error:",reactionId, "is the objective function and has no reactants")
                quit()
            # warn user if no reactants
            elif listOfReactants== None :
                print("Warning:",reactionId, "listOfReactants=None")
            # else make facts for each reactant
            else:
                for r in listOfReactants:
                    reactantId = r.attrib.get("species")
                    # define reactant diferently if reaction is objective function
                    if obj_fnct and prefix == 'd':
                        targets.append(reactantId)
                        lpfacts.append(clingo.Function('rct', [reactantId,r.attrib.get("stoichiometry"), reactionId, clingo.Function('t')]))

                        try:
                            lpfacts.append(clingo.Function('metabolite', [reactantId, clingo.Function('t')]))
                        except KeyError:
                            print('Error: reactant ' + reactantId + ' of the objective reaction '+ reactionId + ' is not defined in list of species')
                            quit()
                        # add it in added species if it was not already in there
                        if not reactantId in added_species:
                            added_species.append(reactantId)

                    # else just add the reactant
                    else:
                        lpfacts.append(clingo.Function('rct', [reactantId,r.attrib.get("stoichiometry"), reactionId, clingo.Function(prefix)]))
                        if not reactantId in added_species:
                            lpfacts.append(clingo.Function('metabolite', [reactantId, clingo.Function(prefix)]))
                            added_species.append(reactantId)



            # get products of considered reaction
            listOfProducts = get_listOfProducts(e)
            # warn user if no products
            if listOfProducts== None :
                print("\n Warning:",reactionId, "listOfProducts=None")
            else:
                for p in listOfProducts:
                    productId = p.attrib.get("species")
                    # define product diferently if reaction is objective function
                    if obj_fnct and prefix == 'd':
                        lpfacts.append(clingo.Function('prd', [productId, p.attrib.get("stoichiometry"), reactionId,clingo.Function('t')]))
                        #lpfacts.append(clingo.Function('t_compound', [productId, p.attrib.get("stoichiometry"), reactionId]))
                        # add the t_compound

                    # else just add the product
                    else:
                        lpfacts.append(clingo.Function('prd', [productId, p.attrib.get("stoichiometry"), reactionId, clingo.Function(prefix)]))
                        # add the r_compound or d_compound in the facts if not already done for this compound

                    # add the r_compound or d_compound if not already done for this compound
                    if not productId in added_species:
                        #print(reactantId, prefix)
                        try:
                            lpfacts.append(clingo.Function('metabolite', [productId, clingo.Function(prefix)]))
                            added_species.append(productId)
                        except KeyError:
                            added_species.append(productId)
                            #print(productId, reactionId)
                            pass


    #some checks to alert the user
    if prefix == "d":
        # no reaction has an objective coefficient 1
        if objective_reactions == []:
            print("\n Error in model: no defined objective function")
            quit()
        # several reactions have an objective reaction 1 : warn user, might not be wanted
        elif len(objective_reactions) > 1:
            print("\n Warning: > 1 objective reactions are defined " + str(objective_reactions))
        # no seeds are given
        if len(seeds) == 0:
            print("\n Error in model: no defined boundaryCondition = \"true\" species in ListOfSpecies. Please make the growth medium compounds at boundaryCondition = \"true\" ")
            #quit()

    #check whether we added every compound (t_, r_, d_)
    if len(added_species) != len(species_data):
        if prefix =='d':
            print('DRAFT')
        else:
            print('REPAIR NETWORK')
        print('Warning: your list of species is not consistant with the list of reactants and products occurring in every reaction')
        extra_los = [x for x in species_data.keys() if not x in added_species]
        extra_reactant_or_product = [x for x in added_species if not x in species_data.keys()]
        if extra_los != [] :
            print('Compounds defined in listOfSpecies but not used in reactions: ' + str(extra_los))
        if extra_reactant_or_product != [] :
            print('Compounds defined as reactants or products in listOfReactions but not in listOfSpecies: ' + str(extra_reactant_or_product))
        print('This warning may lead to altered results during solving, you should correct it. \n')



    # print( "targets: " + str(targets))
    # print( "seeds: " + str(seeds))

    return lpfacts, seeds, targets, objective_reactions