require 'active_support/core_ext/class/attribute'
require_relative 'property.rb'


module Properties
    class ValueAlias < Property
        class_attribute :initial_value, :parent_class

        def self.value
            return self.initial_value
        end

        def become
            if not owner.is? self.parent_class then
                owner.make(self.parent_class)
            end
            self.parent_class.purge_value_aliases(owner, self.class)
            owner.get_property(self.parent_class).set_value(self.initial_value, false)
            super
        end
    end

    class ValueProperty < Property
        class_attribute :initial_value, :value_aliases
        attr_accessor :value

        self.value_aliases = {}

        def self.value
            self.initial_value
        end

        def self.add_alias(name, initial_value)
            alias_class = Class.new(ValueAlias)
            alias_class.initial_value = initial_value
            alias_class.parent_class = self

            Properties.const_set(name, alias_class)
            value_aliases[initial_value] = alias_class
        end

        def self.values=(hash)
            self.value_aliases = []
            hash.each do |name, value|
                self.add_alias(name, value)
            end
        end

        def self.purge_value_aliases(thing, ignore)
            self.value_aliases.each do |value, alias_class|
                thing.unmake(alias_class, force: true) if alias_class != ignore
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

        def >=(other)
            return self.value >= other.value
        end

        def <=(other)
            return self.value <= other.value
        end

        def ==(other)
            return self.value == other.value
        end

        def !=(other)
            return self.value == other.value
        end
    end

    class IntValueProperty < ValueProperty
        def self.values=(array)
            self.value_aliases = {}
            array.each_with_index do |name, index|
                self.add_alias(name, index)
            end
        end
    end
end
