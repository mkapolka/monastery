require 'active_support/core_ext/class/attribute'
require 'set'
require_relative 'property.rb'
require_relative 'value_property.rb'
require_relative 'container.rb'

module Properties
    class Size < ValueProperty
        self.values = {
            'Tiny' => 0,
            'Small' => 1,
            'Big' => 2,
            'Huge' => 3,
        }
    end

    class Hard < Property 
        self.description = "is hard"
        self.types = [Physical]
        self.revealed_by = [Touch, Sight]

        def make()
            owner.say("#{owner.name} becomes hard")
        end
    end

    class Flammable < Property
        self.description = 'is flammable'
        self.types += [Physical]
        self.revealed_by = [ChemistryKnowledge]

        def touch(this, other)
            if other.is?(Burning)
                this.make(Burning)
            end
        end
    end

    class Burning < Property
        self.description = 'is on fire'
        self.types = [Physical]
        self.revealed_by = [Sight]

        def make()
            this.say("#{this.name} catches on fire!", Sight)
        end

        def tick
            if this.random(0.5) then
                this.unmake(Burning)
            end
        end
    end

    class Hot < Property
        self.description = 'is hot'
        self.types = [Physical]
        self.revealed_by = [Touch]
    end

    class Poisonous < Property
        self.description = 'is poisonous'
        self.types = [Chemical]
        self.revealed_by = [Touch]
    end

    class Edible < Property
        self.description = 'is edible'
        self.types = [Physical]
        self.revealed_by = [ChemistryKnowledge]

        def digest(me, digester)
            me.say("#{me.name} was dissolved into insubstantial mush")
            #me.destroy
        end
    end

    class Soluble < Property
        self.description = 'can be dissolved into liquids'
        self.types = [Physical]
        self.revealed_by = [ChemistryKnowledge]

        def touch(other)
            if other.is? Liquid, Hot
                if me.random(3)
                    me.say("#{me.name} dissolves into #{other.name}")
                    me.properties(Chemical).each do |property|
                        
                    end
                end
            end
        end
    end

    class Ossifying < Property
        self.description = 'is turning into stone'
        self.types = [Physical]
        self.revealed_by = [Sight, ChemistryKnowledge]

        def tick
            if rand(10) == 1
                p "#{me.name} hardens"
                me.material = Materials::Stone
            end
        end
    end

    class Liquid < Property
        self.description = 'is a liquid'
        self.types = [Physical]
        self.revealed_by = [Sight, Touch]

        def make()
            #self.owner.unmake(property_class) if property_class.types.index Mechanical
        end

        def added_to(place)
            liquid = place.contents.find{|thing| thing.is? Liquid and thing != owner}
            if liquid then
                #Combine this with the other
                owner.say("#{owner.name} merges with #{liquid.name}")
                properties = owner.properties(Chemical).values - liquid.properties(Chemical).values
                properties.each do |property|
                    owner.make(property.class)
                end
                liquid.move(nil)
            end
        end
    end

    class Boilable < Property
        self.description = 'can boil'
        self.types = [Physical]
        self.revealed_by = [ChemistryKnowledge]

        def tick
            if owner.is? Hot and owner.not? Boiling and self.random(10, 0.5) then
                owner.say("#{owner.name} begins to boil.")
                owner.make(Boiling)
            end
        end
    end

    class Boiling < Property
        self.description = 'is boiling'
        self.types = [Physical]
        self.revealed_by = [Sight, Touch]
    end

    class Brittle < Property
        self.description = 'is brittle'
        self.types = [Physical]
        self.revealed_by = [Sight, Touch, ChemistryKnowledge]
        
        def bash(basher)
            self.owner.say("#{self.owner.name} shatters into pieces!")
        end

        def churn(churner)
            self.owner.say("#{self.owner.name} is ground into dust")
        end
    end

    class Hollow < Place
        self.description = 'is hollow'
        self.types = [Mechanical]
        self.revealed_by = [Sight, Touch]
    end
end
