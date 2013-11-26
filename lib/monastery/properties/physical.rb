require 'active_support/core_ext/class/attribute'
require 'set'
require_relative 'property.rb'
require_relative 'value_property.rb'
require_relative 'container.rb'

module Properties
    class Boilable < Property
        self.description = 'can boil'
        self.types = [Physical]
        self.revealed_by = [ChemistryKnowledge]

        def tick
            if owner.is? Temperature and owner.temperature >= Hot and owner.not? Boiling and self.random(10, 0.5) then
                owner.say("#{owner.name} begins to boil.")
                owner.make(Boiling)
            end
        end
    end

    class Boiling < Property
        self.description = 'is boiling'
        self.types = [Physical]
        self.revealed_by = [Sight, Touch]

        def tick
            if owner.is? Temperature and owner.temperature < Hot and self.random(10, 0.5) then
                owner.say("#{owner.name} stops boiling.")
                owner.unmake Boiling
            end
        end
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

    class Edible < Property
        self.description = 'is edible'
        self.types = [Physical]
        self.revealed_by = [ChemistryKnowledge]

        def digest(me, digester)
            me.say("#{me.name} was dissolved into insubstantial mush")
            me.destroy
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

    class Hard < Property 
        self.description = "is hard"
        self.types = [Physical]
        self.revealed_by = [Touch, Sight]

        def make()
            owner.say("#{owner.name} becomes hard")
        end
    end

    class Hollow < Container
        self.description = 'is hollow'
        self.types = [Mechanical]
        self.revealed_by = [Sight, Touch]
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
                if liquid.is? Size and owner.is? Size then
                    bigger = liquid.size > owner.size ? liquid : owner
                else
                    bigger = rand() < 0.5 ? liquid : owner
                end
                smaller = bigger == liquid ? owner : liquid
                #Combine this with the other
                owner.say("#{smaller.name} merges with #{bigger.name}")
                properties = bigger.properties(Chemical).values - smaller.properties(Chemical).values
                properties.each do |property|
                    bigger.make(property.class)
                end
                smaller.destroy
            end
        end
    end

    class Open < Property
        self.description = 'is open'
        self.types = [Mechanical]
        self.revealed_by = [Sight, Touch]
    end

    class Openable < Property
        self.description = 'can be opened'
        self.types = [Mechanical]
        self.revealed_by = [Sight, Touch]

        def open
            owner.make Open if owner.not? Open
        end

        def close
            owner.unmake Open if owner.is? Open
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

    class Poisonous < Property
        self.description = 'is poisonous'
        self.types = [Chemical]
        self.revealed_by = [Touch]
    end

    class Size < IntValueProperty
        self.values = [
            'Tiny',
            'Small',
            'AverageSize',
            'Big',
            'Huge',
        ]
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

    class Temperature < IntValueProperty
        self.values = [
            'Cold',
            'Cool',
            'AverageTemperature',
            'Warm',
            'Hot'
        ]
    end

    class Waterproof < Property
        self.description = 'is waterproof'
        self.types = [Physical]
        self.revealed_by = [Sight, Touch]
    end

end
