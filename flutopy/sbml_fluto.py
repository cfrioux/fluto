#!/usr/bin/python


import time
import xml.etree.ElementTree as etree
import clingo
import logging
logger = logging.getLogger(__name__)


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
        if tag == "kineticLaw":
            kineticLaw = e
            for ee in kineticLaw:
                if ee.tag[0] == "{":
                    uri, tag = ee.tag[1:].split("}")
                else:
                    tag = ee.tag
                if tag == "listOfParameters":
                    listOfParameters = ee
                    break
    return listOfParameters


def readSBMLnetwork(filename, prefix):
    """ create lp facts for the network from SBML """

    lpfacts = []
    tree = etree.parse(filename)
    sbml = tree.getroot()
    model = get_model(sbml)
    listOfReactions = get_listOfReactions(model)
    listOfSpecies = get_listOfSpecies(model)

    seeds = []
    targets = []
    objective_reactions = []
    species_data = {}
    added_species = []

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
                lpfacts.append(clingo.Function(
                    'metabolite', [speciesId, clingo.Function('s')]))
                if not speciesId in species_data:
                    species_data[speciesId] = {
                        'compartment': speciesCp, 'boundaryCondition': speciesBC}
                else:
                    logger.error('Error: compound ' +
                                 speciesId + 'is defined twice')
                    quit()
            else:
                if not speciesId in species_data:
                    species_data[speciesId] = {
                        'compartment': speciesCp, 'boundaryCondition': speciesBC}
                else:
                    logger.error('Error: compound ' +
                                 speciesId + 'is defined twice')
                    quit()

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
                logger.warning(
                    'set default parameters for repairDB reaction {0}'.format(reactionId))
            elif listOfParameters == None:
                logger.error(
                    "Error in draft reaction: {reactionId} listOfParameters = None")
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
                logger.warning("No lower bound defined for reaction {reactionID}. Set lower bound to default value" +
                               str(default_lb))

            if ub == None:
                ub = default_ub
                logger.warning("No upper bound defined for reaction {reactionID}. Set upper bound to default value " +
                               str(default_ub))

            if (lb < 0 and ub > 0) or (lb > 0 and ub < 0):
                lpfacts.append(clingo.Function('reversible', [reactionId]))

            if oc == None:
                oc = default_oc
                logger.warn("No objective coefficient defined for reaction {reactionId}. Set objective coefficient to default value " +
                            str(default_oc))

            # make facts for an objective reaction
            if obj_fnct and prefix == 'd':
                lpfacts.append(clingo.Function(
                    'reaction', [reactionId, clingo.Function('t')]))
                lpfacts.append(clingo.Function(
                    'objective', [reactionId, clingo.Function('t')]))
                lpfacts.append(clingo.Function(
                    'bounds', [reactionId, str(lb), str(ub)]))

            # make facts for a regular reaction
            else:
                lpfacts.append(clingo.Function(
                    'reaction', [reactionId, clingo.Function(prefix)]))
                lpfacts.append(clingo.Function(
                    'objective', [reactionId, clingo.Function(prefix)]))
                lpfacts.append(clingo.Function(
                    'bounds', [reactionId, str(lb), str(ub)]))

            # get reactants of considered reactin
            listOfReactants = get_listOfReactants(e)

            # warn user if no reactants
            if listOfReactants == None:
                logger.warning("Warning: {reactionId} listOfReactants=None")

                # exit with error if no reactant for an objective function
                if obj_fnct == True:
                    logger.error(
                        "error: {reactionId} is used in the objective function and has no reactants")
                    quit()

            # else make facts for each reactant
            else:
                for r in listOfReactants:
                    reactantId = r.attrib.get("species")
                    # define reactant diferently if reaction is objective function
                    if obj_fnct and prefix == 'd':
                        targets.append(reactantId)
                        lpfacts.append(clingo.Function('rct', [reactantId, r.attrib.get(
                            "stoichiometry"), reactionId, clingo.Function('t')]))

                        try:
                            lpfacts.append(clingo.Function(
                                'metabolite', [reactantId, clingo.Function('t')]))
                        except KeyError:
                            logger.error(
                                'Error: reactant {reactantId} of the objective reaction {reactionId} is not defined in list of species')
                            quit()
                        # add it in added species if it was not already in there
                        if not reactantId in added_species:
                            added_species.append(reactantId)

                    # else just add the reactant
                    else:
                        lpfacts.append(clingo.Function('rct', [reactantId, r.attrib.get(
                            "stoichiometry"), reactionId, clingo.Function(prefix)]))
                        if not reactantId in added_species:
                            lpfacts.append(clingo.Function(
                                'metabolite', [reactantId, clingo.Function(prefix)]))
                            added_species.append(reactantId)

            # get products of considered reaction
            listOfProducts = get_listOfProducts(e)
            # warn user if no products
            if listOfProducts == None:
                logger.warning("Warning: {reactionId} listOfProducts=None")
            else:
                for p in listOfProducts:
                    productId = p.attrib.get("species")
                    # define product diferently if reaction is objective function
                    if obj_fnct and prefix == 'd':
                        lpfacts.append(clingo.Function('prd', [productId, p.attrib.get(
                            "stoichiometry"), reactionId, clingo.Function('t')]))
                        # lpfacts.append(clingo.Function('t_compound', [productId, p.attrib.get("stoichiometry"), reactionId]))
                        # add the t_compound

                    # else just add the product
                    else:
                        lpfacts.append(clingo.Function('prd', [productId, p.attrib.get(
                            "stoichiometry"), reactionId, clingo.Function(prefix)]))
                        # add the r_compound or d_compound in the facts if not already done for this compound

                    # add the r_compound or d_compound if not already done for this compound
                    if not productId in added_species:

                        try:
                            lpfacts.append(clingo.Function(
                                'metabolite', [productId, clingo.Function(prefix)]))
                            added_species.append(productId)
                        except KeyError:
                            added_species.append(productId)
                            pass

    # some checks to alert the user
    if prefix == "d":
        # no reaction has an objective coefficient 1
        if objective_reactions == []:
            logger.error("Error in model: no defined objective function")
            quit()
        # several reactions have an objective reaction 1 : warn user, might not be wanted
        elif len(objective_reactions) > 1:
            logger.warning("Warning: > 1 objective reactions are defined " +
                           str(objective_reactions))
        # no seeds are given
        if len(seeds) == 0:
            logger.error(
                "Error in model: no defined boundaryCondition = \"true\" species in ListOfSpecies. Please make the growth medium compounds at boundaryCondition = \"true\" ")

    # check whether we added every compound (t_, r_, d_)
    if len(added_species) != len(species_data):
        if prefix == 'd':
            logger.warning('DRAFT')
        else:
            logger.warning('REPAIR NETWORK')
        logger.warning(
            'Warning: your list of species is not consistent with the list of reactants and products occurring in every reaction')
        extra_los = [x for x in species_data.keys() if not x in added_species]
        extra_reactant_or_product = [
            x for x in added_species if not x in species_data.keys()]
        if extra_los != []:
            logger.warning(
                'Compounds defined in listOfSpecies but not used in reactions: ' + str(extra_los))
        if extra_reactant_or_product != []:
            logger.warning('Compounds defined as reactants or products in listOfReactions but not in listOfSpecies: ' +
                           str(extra_reactant_or_product))
        logger.warning(
            'This may lead to altered results during solving, you should correct it.')

    return lpfacts, seeds, targets, objective_reactions
