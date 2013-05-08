class Object
   #Get the metaclass / eigenclass
   def metaclass; class << self; self; end; end
end

class Noun
   attr_accessor :adjectives, :name, :parent
   attr_reader :responders

   class << self
      attr_accessor :class_adjectives
      class_adjectives = [];
   end

   def initialize
      @name = "#{self.class}"
      @adjectives = {};
      @responders = {};

      self.class.class_adjectives.uniq.each do |c|
         make(c);
      end
   end

   def add_responder(event, responder)
      @responders[event] ||= [];
      @responders[event] << responder;
   end

   def remove_responder(event, &block)
      @responders[event].splice(responder)
   end
   
   def call_responders(event, *args)
      return if @responders[event].nil?
      @responders[event].each do |adj|
         puts adj
         puts adj.events
         adj.call(adj.events[event],args) if not adj.events.nil?
      end
   end

   def do(what, *args)
      @adjectives.each do |adj|
         adj.call(what, args) if (adj.respond_to? what)
      end
   end

   def make(adjective)
      adj_class = Adjectives.const_get(adjective.capitalize) if adjective.class == Symbol;
      unless adjectives[adjective].nil?
         adjectives[adjective].count += 1 
      else 
         a = adjectives[adjective] = adj_class.new
         a.noun = self;

         metaclass.instance_eval do 
            define_method(adjective.downcase) do
               adjectives[adjective]
            end

            define_method(adjective.downcase.to_s + "?") do
               !adjectives[adjective].nil?
            end
         end
      end
   end
   alias :becomes :make

   def adjectives_of_type(type)
      return adjectives.each_pair.map do |key, value|
         #!value.types.index(type).nil? 
         value if !value.types.index(type).nil?
      end
   end

   def method_missing(method, *args)
      puts "Mizzing"
      return false if (method[-1] == "?")
      super.method_missing(method, args)
   end

   def describe
      "The #{name}" + adjectives.values.reduce(""){ |p,x| p + " " + x.describe + " and" }[0...-4] + "."
   end

   def is?(adjective)
      not adjectives[adjective.downcase.to_sym].nil?;
   end

   def self.is(*adjectives)
      adjectives.each do |adj|
         if (not Adjectives.const_defined?(adj.capitalize))
            puts "Unrecognized adjective '#{adj}' in #{self} definition.";
         else
            self.class_adjectives ||= [];
            self.class_adjectives.push(adj);
         end
      end
   end
end

class Bear < Noun
   is :fuzzy
end

class Tea_Kettle < Noun
   is :container, :hard
end
