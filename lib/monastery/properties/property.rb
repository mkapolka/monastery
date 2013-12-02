require 'active_support/core_ext/class/attribute'
require 'active_support/inflector'
require 'monastery/constants.rb'
require 'monastery/lookup.rb'

module Templates
end

module Properties
    class Property
        finds_constants_in Templates, PropertyTypes, RevealMethods, Actions

        class_attribute :description, :types, :revealed_by
        attr_accessor :owner

        self.description = "has a property"
        self.types = []
        self.revealed_by = []

        attr_accessor :count

        def initialize
            @count = 0
            @random_aggregators = {}
        end

        def describe
            return "#{owner.name} #{self.class.description}"
        end

        def revealed_by?(method)
            return revealed_by.include?(method)
        end

        def random(calls, randomness, aggregator: :default)
            @random_aggregators[aggregator] ||= 0.0
            @random_aggregators[aggregator] += (rand() * randomness.to_f) * 2 + (1 - randomness)

            if @random_aggregators[aggregator] > calls then
                @random_aggregators[aggregator] = 0.0
                return true
            else
                return false
            end
        end

        def make(property_class)
        end

        def unmake(property_class)
        end

        def become
        end

        def cease
        end

        def inspect
            return "Property(#{self.class.name.demodulize})"
        end

        #The key that will be used in the containing Thing's 
        # property dict to find this property
        def self.key
            return self.name.demodulize.to_sym
        end
    end
end
