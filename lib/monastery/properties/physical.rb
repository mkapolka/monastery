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

        def merge_with(other_liquid)
            if other_liquid.is? Size and owner.is? Size then
                bigger = other_liquid.size > owner.size ? other_liquid : owner
            else
                bigger = rand() < 0.5 ? other_liquid : owner
            end
            smaller = bigger == other_liquid ? owner : other_liquid
            #Combine this with the other
            owner.say("#{smaller.name} merges with #{bigger.name}")
            properties = bigger.properties(Chemical).values - smaller.properties(Chemical).values
            properties.each do |property|
                bigger.make(property.class)
            end
            smaller.destroy
        end

        def added_to(place)
            liquid = place.contents.find{|thing| thing.is? Liquid and thing != owner}
            #Merge with other liquids
            if liquid then
                merge_with(liquid)
            end

            #Fall out if the container isn't waterproof
            if place.instance_of? Container
                if place.not? Watertight
                    owner.say "#{owner.name} seeps through #{place.owner.name}"
                    owner.move place.owner.location
                end
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
                if self.random(3, 1)
                    owner.say("#{me.name} dissolves into #{other.name}")
                    owner.properties(Chemical).each do |property|
                        other.make(property.class)
                        self.destroy
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

    class Watertight < Property
        self.description = 'is waterproof'
        self.types = [Physical]
        self.revealed_by = [Sight, Touch]
    end

end
