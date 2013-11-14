require 'active_support/core_ext/class/attribute'
require 'active_support/inflector'
require_relative '../lookup.rb'

module Templates
end

module Properties
    class Property
        finds_constants_in Templates

        class_attribute :description, :types, :revealed_by
        attr_accessor :owner

        self.description = "has a property"
        self.types = []
        self.revealed_by = []

        attr_accessor :count

        def initialize
            @count = 0
        end

        def describe(what)
            return "#{what.name} #{self.class.description}"
        end

        def revealed_by?(method)
            return revealed_by.include?(method)
        end

        def random(chance, randomness)
            return Math.random(1) < chance
        end

        def make(me)
            self.owner = me
        end

        def unmake(me)
            self.owner = nil
        end

        def inspect
            return self.class.name.demodulize
        end

        #The key that will be used in the containing Thing's 
        # property dict to find this property
        def self.key
            return self.name.demodulize.to_sym
        end
    end
end
