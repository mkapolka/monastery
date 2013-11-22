require 'monastery/properties/all.rb'
require_relative 'template.rb'
require_relative 'materials.rb'

module Templates
    class Template
        extend Properties::AdverbMakers
    end

    class Apple < Template
        self.name = "an apple"
        self.properties = [Flammable]
    end

    class MagicApple < Template
        self.name = "a magic apple"
        self.properties = [Hard, Flammable, magically(Poisonous)]
    end

    class MagicPear < Template
        self.name = "a magic pear"
        self.properties = [Flammable, magically(Poisonous)]
    end

    class TeaKettle < Template
        material(Metal)
        self.name = "a tea kettle"
        self.properties += [Hollow]
        self.contains_in(Hollow, MagicPear)
    end

    class Water < Template
        self.name = "some water"
        self.properties = [Liquid, Boilable]
    end

    class Poison < Template
        material(Water)
        self.name = "some poison"
        self.properties += [Poisonous]
    end
end
