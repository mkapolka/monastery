require 'active_support/inflector'
require 'active_support/core_ext/array/conversions'

module Properties
    module AdverbMakers
        def magically(property_class)
            class_name = "Magically_#{property_class.name.demodulize}"
            if not Properties.const_defined? class_name then
                magic_class = Class.new(Magically) do
                    self.gives_property = property_class
                end
                Properties.const_set(class_name, magic_class)
                return magic_class
            else
                return Properties.const_get(class_name)
            end
        end
    end

    class Magically < Property
        class_attribute :gives_property

        self.types += [:magical]
        self.revealed_by += [:magical_knowledge]

        def describe
            return "by wizardly forces is #{properties.to_sentence}"
        end

        def make(who)
            who.make gives_property
        end

        def unmake(who)
            who.unmake gives_property
        end
    end

    # Second take on 'magically' adverb
    # Define a new class that doesn't inherit the given class but instead
    # adds the given class along side it

    class Becoming < Property
        class_attribute :future_property
        def tick(me)
            if (rand(5)) then
                me.make(self.future_property)
            end
        end
    end

    def becoming(property_class)
        class_name = "Becoming_#{property_class.name.demodulize}"
        if not Properties.const_defined? class_name then
            bc_class = Class.new(Becoming) do
                self.future_property = property_class
            end
            Properties.const_set(class_name, bc_class)
        else
            return Properties.const_get(class_name)
        end
    end
end
