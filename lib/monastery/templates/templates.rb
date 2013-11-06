require 'monastery/properties/all.rb'
require_relative 'template.rb'

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
        self.properties = [Hard, Flammable, magically(Poisonous)]
    end
end
