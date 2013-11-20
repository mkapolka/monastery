require 'active_support/core_ext/class/attribute'
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
        self.types = [:physical]

        def make()
            owner.say("#{owner.name} becomes hard")
        end
    end

    class Flammable < Property
        self.description = 'is flammable'
        self.types += [:physical]
        self.revealed_by = [:chemical_knowledge]

        def touch(this, other)
            if other.is?(Burning)
                this.make(Burning)
            end
        end
    end

    class Burning < Property
        self.description = 'is on fire'
        self.types = [:physical]
        self.revealed_by = [:sight]

        def make(this)
            this.say("#{this.name} catches on fire!", :sight)
        end

        def tick(this)
            if this.random(0.5) then
                this.unmake(Burning)
            end
        end
    end

    class Hot < Property
        self.description = 'is hot'
        self.types = [:physical]
        self.revealed_by = [:touch]
    end

    class Poisonous < Property
        self.description = 'is poisonous'
        self.types = [:chemical]
        self.revealed_by = [:feel]
    end

    class Edible < Property
        self.description = 'is edible'
        self.types = [:physical]
        self.revealed_by = [:chemical_knowledge]

        def digest(me, digester)
            me.say("#{me.name} was dissolved into insubstantial mush")
            #me.destroy
        end
    end

    class Soluble < Property
        self.description = 'can be dissolved into liquids'
        self.types = [:physical]
        self.revealed_by = [:chemical_knowledge]

        def touch(other)
            if other.is? Liquid, Hot
                if me.random(3)
                    me.say("#{me.name} dissolves into #{other.name}")
                    me.properties(:chemical).each do |property|
                        
                    end
                end
            end
        end
    end

    class Ossifying < Property
        self.description = 'is turning into stone'
        self.types = [:physical]
        self.revealed_by = [:sight, :chemical_knowledge]

        def tick(me)
            if rand(10) == 1
                p "#{me.name} hardens"
                me.material = Materials::Stone
            end
        end
    end

    class Liquid < Property
        self.description = 'is a liquid'
        self.types = [:physical]
        self.revealed_by = [:sight, :feel]

        def make(property_class)
            self.owner.unmake(property_class) if property_class.types.index :mechanical
        end
    end

    class Boils < Property
        self.description = 'can boil'
        self.types = [:physical]
        self.revealed_by = [:chemical_knowledge]

        def tick
            if owner.is? Hot && owner.not? Boiling && self.random(.1) then
                self.make(Boiling)
            end
        end
    end

    class Boiling < Property
        self.description = 'is boiling'
        self.types = [:physical]
        self.revealed_by = [:sight, :feel]
    end

    class Brittle < Property
        self.description = 'is brittle'
        self.types = [:physical]
        self.revealed_by = [:sight, :feel, :chemical_knowledge]
        
        def bash(basher)
            self.owner.say("#{self.owner.name} shatters into pieces!")
        end

        def churn(churner)
            self.owner.say("#{self.owner.name} is ground into dust")
        end
    end

    class Hollow < Place
        self.description = 'is hollow'
        self.types = [:mechanical]
        self.revealed_by = [:sight, :feel]
    end
end
