module PropertyTypes
    Physical = :physical
    Chemical = :chemical
    Mechanical = :mechanical
end

module RevealMethods
    Sight = :sight
    Touch = :touch
    ChemistryKnowledge = :chemistry_knowledge
end

module Actions
    #Called on all properties when thing.make is called, passed property_class
    Make = :make
    #Called on the specific proprty when thing.is? PropertyClass would return true
    Become = :become
    #Called on all properties when thing.unmake is called, passed property_class
    Unmake = :unmake
    #Called on the specific property when thing.not? PropertyClass would return true
    Cease = :cease
    
    #Place methods
    #Added: Called on the place owner when anything is added to a place
    Added = :added
    #AddedTo: Called on a thing when it's added to a place
    AddedTo = :added_to
    #Removed: Called on the place owner when anything is removed from the place
    Removed = :removed
    #RemovedFrom: Called on a thing when it's removed from a place
    RemovedFrom = :removed_from

    #When two things touch
    Touch = :touch
end
