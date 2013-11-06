require 'active_support/core_ext/class/attribute'
require_relative 'property.rb'
require_relative 'value_property.rb'

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
        self.types += [:physical, :donk]

        def make(this)
            this.say("#{this.name} becomes hard")
        end
    end

    class Flammable < Property
        self.description = 'is flammable'
        self.types += [:physical]
        self.revealed_by = [:chemical_knowledge]

        def test()
            p Burning
            p Templates::MagicApple
        end

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

        def touch(me, other)
            if other.is? :liquid, :hot
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
end
