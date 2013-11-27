require 'monastery/constants.rb'
require 'monastery/lookup.rb'

class Thing
    finds_constants_in Actions
    attr_accessor :properties, :name, :description

    def initialize
        @properties = {}
        @name = "a thing"
        @description = ""
    end

    def inspect
        return "Thing(#{name})"
    end

    def destroy
        self.properties.values.each do |property|
            property.cease
            property.owner = nil
        end
        self.properties.clear
    end

    def method_missing(method_name, *args, &block)
        #Nice way of getting at properties
        return @properties[method_name] if @properties.has_key? method_name
        return @properties[method_name.capitalize] if @properties.has_key? method_name.capitalize
        super
    end

    def properties(types=nil)
        return @properties if types == nil
        return @properties.select{|key, property| property.types.include? types}
    end

    def get_property(property_class)
        return @properties[property_class.key]
    end

    def set_property(property_class, property_object)
        property_object.owner = self
        @properties[property_class.key] = property_object
    end

    def delete_property(property_class)
        property_object.owner = nil
        @properties.delete property_class.key
    end

    def has_property?(property_class)
        @properties.include? property_class.key
    end

    def make(property_class)
        if self.has_property? property_class
            property = get_property(property_class)
            property.count += 1
        else
            property = property_class.new
            property.count = 1
            set_property(property_class, property)
            property.become
        end

        properties.each do |key, value|
            property.make(property_class)
        end
    end

    def unmake(property_class, force: false)
        property_key = property_class.key
        if self.has_property? property_class
            prop = self.get_property(property_class)
            if not force
                prop.count -= 1
            else
                prop.count = 0
            end

            if prop.count == 0 then
                prop.cease()
            end
            
            self.properties.each do |key, property|
                property.unmake(property_class)
            end
        end
    end

    def call(method_name, args=nil)
        self.properties.each do |key, property|
            property.send(method_name, *args) if property.class.method_defined? method_name
        end
        clear_unmade_properties
    end

    def clear_unmade_properties
        self.properties.reject!{|key, value| value.count == 0}
    end

    def is?(property_class)
        has_property?(property_class) && self.get_property(property_class).count > 0
    end

    def not?(property_class)
        not is? property_class
    end

    def describe(method)
        description = ""
        properties.values.each do |property|
            if property.revealed_by? method
                description += property.describe
            end
        end
        return description
    end

    def say(message)
        puts message
    end
    
    def materials=(material_class)
        material_class.apply(self)
    end

    def contents(types=nil)
        output = []
        if types.nil? then
            places = self.properties types
        else
            places = self.properties.values
        end

        places.values.each do |place|
            output.concat(place.contents) if place.class < Place
        end

        return output
    end
end
