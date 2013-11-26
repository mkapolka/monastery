require 'active_support/core_ext/class/attribute'
require 'monastery/thing.rb'
require 'monastery/lookup.rb'

module Properties; end

module Templates
    class Template
        finds_constants_in Properties
        
        class_attribute :properties, :name, :description, :contents

        self.properties = []
        self.name = "a thing"
        self.description = "This is a thing"

        def self.apply(thing)
            self.properties.each do |property|
                thing.make(property)
            end

            if self.contents != nil then
                self.contents.each do |place, templates|
                    templates.each do |template|
                        content = template.create
                        content.move(thing.get_property place)
                    end
                end
            end
        end

        def self.unapply(thing)
            self.properties each do |property|
                thing.unmake(property)
            end
        end

        def self.swap(thing, other_template)
            remove = other_template.properties - self.properties
            add = self.properties - other_template.properties

            remove.each do |property|
                thing.unmake property
            end

            add.each do |property|
                thing.make property
            end
        end

        def self.create
            thing = Thing.new
            thing.name = self.name
            thing.description = self.description

            self.apply(thing)

            return thing
        end

        def self.mixin(template)
            self.properties += template.properties
        end

        def self.contains_in(place, *things)
            self.contents ||= {}
            self.contents[place] ||= []
            self.contents[place] += things
        end
    end

    class UniqueSubtemplate < Template
        class_attribute :container_property

        def apply(thing)
            super thing
            thing.get_property(self.container_property).subtemplate = self
        end

        def unapply(thing)
            super thing
            thing.get_property(self.container_property).subtemplate = nil
        end
    end
end
