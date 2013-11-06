require 'active_support/core_ext/class/attribute'
require_relative 'property.rb'


module Properties
    class ValueAlias < Property
        class_attribute :initial_value, :parent_class

        def make(me)
            if not me.is? self.parent_class then
                me.make(self.parent_class)
            end
            self.parent_class.purge_value_aliases(me, self.class)
            me.get_property(self.parent_class).set_value(self.initial_value, false)
            super
        end
    end

    class ValueProperty < Property
        class_attribute :initial_value, :value_aliases
        attr_accessor :value

        def self.values=(hash)
            self.value_aliases = {}
            hash.each do |name, value|
                alias_class = Class.new(ValueAlias)
                alias_class.initial_value = value
                alias_class.parent_class = self

                Properties.const_set(name, alias_class)
                self.value_aliases[value] = alias_class
            end
        end

        def self.purge_value_aliases(thing, ignore)
            self.value_aliases.each do |value, alias_class|
                thing.delete_property(alias_class) if alias_class != ignore
            end
        end

        def set_value(new_value, do_callbacks=false)
            if self.value_aliases[@value] and self.owner != nil and do_callbacks then
                owner.unmake(self.value_aliases[@value])
            end
            @value = new_value
            if self.value_aliases[@value] and self.owner != nil and do_callbacks then
                owner.make(self.value_aliases[@value])
            end
        end

        def value=(new_value)
            self.set_value(new_value, true)
        end

        def <(other)
            return self.value < other.value
        end

        def >(other)
            return self.value > other.value
        end

        def ==(other)
            return self.value == other.value
        end

        def !=(other)
            return self.value == other.value
        end
    end
end
